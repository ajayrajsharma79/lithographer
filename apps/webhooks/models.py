import uuid
import hmac
import hashlib
import json
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Consider defining event choices centrally if they become numerous
# EVENT_CHOICES = [ ('content.published', 'Content Published'), ... ]

class WebhookEndpoint(models.Model):
    """
    Represents a configured endpoint to send webhook notifications to.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_url = models.URLField(
        _("Target URL"),
        max_length=500, # Increased length for potentially long URLs with params
        help_text=_("The URL where the webhook payload should be sent.")
    )
    # Using JSONField for flexibility in defining subscribed events initially.
    # A ManyToManyField to a dedicated EventType model could be used for more structure.
    subscribed_events = models.JSONField(
        _("Subscribed Events"),
        default=list, # Example: ["content.published", "user.created", "*"]
        blank=True,
        help_text=_("List of event types this webhook listens for (e.g., ['content.published', 'user.created']). Use '*' for all events.")
    )
    secret = models.CharField(
        _("Webhook Secret"),
        max_length=255,
        help_text=_("A secret key used to sign the webhook payload for verification on the receiver's end."),
        # Consider storing secrets more securely (e.g., encrypted field or external vault)
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Whether this webhook endpoint is currently active and should receive events.")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Link to CMSUser
        on_delete=models.SET_NULL, # Keep endpoint if user is deleted
        null=True,
        blank=True,
        related_name="webhook_endpoints",
        verbose_name=_("Created By")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Webhook Endpoint")
        verbose_name_plural = _("Webhook Endpoints")
        ordering = ['-created_at']

    def __str__(self):
        return self.target_url

    def generate_signature(self, payload_body):
        """Generates HMAC-SHA256 signature for the payload."""
        if not self.secret:
            return None # Cannot sign without a secret
        # Ensure payload_body is bytes
        if isinstance(payload_body, str):
            payload_body = payload_body.encode('utf-8')
        mac = hmac.new(self.secret.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
        return mac.hexdigest()


class WebhookEventLog(models.Model):
    """
    Logs the delivery attempt of a specific webhook event.
    """
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_SUCCESS, _('Success')),
        (STATUS_FAILED, _('Failed')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE, # If endpoint is deleted, logs are too
        related_name="event_logs",
        verbose_name=_("Webhook Endpoint")
    )
    event_type = models.CharField(
        _("Event Type"),
        max_length=100,
        db_index=True,
        help_text=_("The specific event that triggered this webhook (e.g., 'content.published').")
    )
    payload = models.JSONField(
        _("Payload"),
        help_text=_("The JSON data sent in the webhook request.")
    )
    # Store request headers sent (e.g., signature)
    request_headers = models.JSONField(
        _("Request Headers"),
        null=True, blank=True,
        help_text=_("Headers sent with the webhook request.")
    )
    response_status_code = models.PositiveIntegerField(
        _("Response Status Code"),
        null=True,
        blank=True,
        help_text=_("HTTP status code received from the target URL.")
    )
    # Store response headers received
    response_headers = models.JSONField(
        _("Response Headers"),
        null=True, blank=True,
        help_text=_("Headers received in the webhook response.")
    )
    response_body = models.TextField(
        _("Response Body"),
        blank=True,
        help_text=_("Response body received from the target URL (may be truncated).")
    )
    status = models.CharField(
        _("Delivery Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )
    timestamp = models.DateTimeField(
        _("Timestamp"),
        default=timezone.now,
        db_index=True,
        help_text=_("When the delivery attempt was made.")
    )
    # Optional: Add duration field
    # duration = models.FloatField(null=True, blank=True, help_text="Request duration in seconds")

    class Meta:
        verbose_name = _("Webhook Event Log")
        verbose_name_plural = _("Webhook Event Logs")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event_type} to {self.endpoint.target_url} ({self.status} at {self.timestamp})"

    @property
    def is_successful(self):
        return self.status == self.STATUS_SUCCESS and self.response_status_code is not None and 200 <= self.response_status_code < 300

# Placeholder for the actual webhook sending logic (likely using Celery)
# def trigger_webhook(event_type, data):
#     endpoints = WebhookEndpoint.objects.filter(is_active=True)
#     # Filter endpoints subscribed to this event_type or '*'
#     # For each endpoint, create a task to send the webhook
#     pass
