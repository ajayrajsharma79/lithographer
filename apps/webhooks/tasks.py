import logging
import requests
import json
import hmac
import hashlib
from celery import shared_task
from django.utils import timezone
from django.conf import settings

from .models import WebhookEndpoint, WebhookEventLog, AVAILABLE_EVENT_NAMES

logger = logging.getLogger(__name__)

# Define webhook request timeout (in seconds)
WEBHOOK_TIMEOUT = 10 # Adjust as needed

@shared_task(bind=True, max_retries=3, default_retry_delay=60) # Add retry logic
def send_webhook(self, event_name, data_payload, endpoint_id):
    """
    Celery task to send a single webhook event to a specific endpoint.
    """
    try:
        endpoint = WebhookEndpoint.objects.get(id=endpoint_id, is_active=True)
    except WebhookEndpoint.DoesNotExist:
        logger.warning(f"Webhook endpoint {endpoint_id} not found or inactive. Skipping.")
        return f"Endpoint {endpoint_id} not found or inactive."

    # Check if endpoint is subscribed to this event
    if "*" not in endpoint.subscribed_events and event_name not in endpoint.subscribed_events:
        logger.info(f"Endpoint {endpoint.target_url} not subscribed to event '{event_name}'. Skipping.")
        return f"Endpoint not subscribed to {event_name}."

    # Prepare payload and headers
    payload = {
        'event': event_name,
        'timestamp': timezone.now().isoformat(),
        'data': data_payload
    }
    try:
        payload_json = json.dumps(payload, sort_keys=True) # Consistent order for signature
    except TypeError:
        logger.error(f"Failed to serialize webhook payload for event {event_name} to {endpoint.target_url}.")
        # Log failure but don't retry serialization errors
        WebhookEventLog.objects.create(
            endpoint=endpoint,
            event_type=event_name,
            payload={'error': 'Payload serialization failed'},
            status=WebhookEventLog.STATUS_FAILED,
        )
        return "Payload serialization failed."

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': f'Lithographer-Webhook-Agent/1.0 (+{settings.SITE_ID})' # Example User-Agent
    }

    # Generate signature if secret exists
    signature = endpoint.generate_signature(payload_json)
    if signature:
        headers['X-Lithographer-Signature-256'] = f"sha256={signature}" # Common signature format

    # Log the attempt (initially pending)
    log_entry = WebhookEventLog.objects.create(
        endpoint=endpoint,
        event_type=event_name,
        payload=payload, # Store the dict payload
        request_headers=headers,
        status=WebhookEventLog.STATUS_PENDING,
    )

    # Make the request
    try:
        logger.info(f"Sending webhook for event '{event_name}' to {endpoint.target_url}")
        response = requests.post(
            endpoint.target_url,
            data=payload_json.encode('utf-8'),
            headers=headers,
            timeout=WEBHOOK_TIMEOUT
        )
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Success
        log_entry.response_status_code = response.status_code
        log_entry.response_headers = dict(response.headers)
        # Limit response body size stored?
        log_entry.response_body = response.text[:2000] # Store first 2000 chars
        log_entry.status = WebhookEventLog.STATUS_SUCCESS
        log_entry.save()
        logger.info(f"Webhook delivered successfully to {endpoint.target_url} (Status: {response.status_code})")
        return f"Success: {response.status_code}"

    except requests.exceptions.Timeout as exc:
        logger.warning(f"Webhook request timed out for {endpoint.target_url}: {exc}")
        log_entry.response_body = f"Request timed out after {WEBHOOK_TIMEOUT} seconds."
        log_entry.status = WebhookEventLog.STATUS_FAILED
        log_entry.save()
        # Retry based on task decorator settings
        raise self.retry(exc=exc)

    except requests.exceptions.RequestException as exc:
        logger.error(f"Webhook request failed for {endpoint.target_url}: {exc}")
        log_entry.response_body = str(exc)
        if exc.response is not None:
            log_entry.response_status_code = exc.response.status_code
            log_entry.response_headers = dict(exc.response.headers)
            # Limit response body size stored?
            log_entry.response_body += "\n\n" + exc.response.text[:2000]
        log_entry.status = WebhookEventLog.STATUS_FAILED
        log_entry.save()
        # Retry based on task decorator settings (especially for 5xx errors)
        if exc.response is not None and 500 <= exc.response.status_code < 600:
             raise self.retry(exc=exc)
        else:
             return f"Failed: {exc}" # Don't retry client errors (4xx) or connection errors immediately

    except Exception as exc:
        # Catch any other unexpected errors during processing
        logger.exception(f"Unexpected error sending webhook to {endpoint.target_url}: {exc}")
        log_entry.response_body = f"Unexpected error: {exc}"
        log_entry.status = WebhookEventLog.STATUS_FAILED
        log_entry.save()
        # Decide whether to retry unexpected errors
        # raise self.retry(exc=exc)
        return f"Unexpected error: {exc}"


@shared_task
def trigger_webhooks_for_event(event_name, data_payload):
    """
    Finds all active endpoints subscribed to an event and queues individual delivery tasks.
    """
    if event_name not in AVAILABLE_EVENT_NAMES:
        logger.warning(f"Attempted to trigger unknown webhook event: {event_name}")
        return f"Unknown event: {event_name}"

    logger.info(f"Triggering webhooks for event: {event_name}")
    # Find endpoints subscribed to this specific event OR the wildcard '*'
    endpoints = WebhookEndpoint.objects.filter(
        models.Q(subscribed_events__contains=event_name) | models.Q(subscribed_events__contains='"*"'),
        is_active=True
    )

    count = 0
    for endpoint in endpoints:
        send_webhook.delay(event_name, data_payload, endpoint.id)
        count += 1

    logger.info(f"Queued {count} webhook delivery tasks for event: {event_name}")
    return f"Queued {count} tasks for {event_name}."