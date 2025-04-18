import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Import models from other apps
from apps.content.models import ContentInstance, STATUS_PUBLISHED
from apps.media.models import MediaAsset

# Import the trigger task
from .tasks import trigger_webhooks_for_event

logger = logging.getLogger(__name__)

# --- ContentInstance Signals ---

@receiver(post_save, sender=ContentInstance)
def content_instance_post_save_handler(sender, instance, created, **kwargs):
    """Trigger webhooks for content updates/publishing."""
    event_name = None
    if created:
        # Potentially trigger 'content_created' if needed, but often
        # 'content_updated' or 'content_published' are more useful.
        pass
    else:
        # Check if status changed to published
        try:
            # Get the previous state if possible (requires tracking or querying DB)
            # Simplified check: if status is now published, trigger event
            if instance.status == STATUS_PUBLISHED:
                 # More robust check needed here to see if it *just* became published
                 event_name = 'content_published'
                 logger.info(f"ContentInstance {instance.id} published, triggering webhook.")
            else:
                 # Assume any other save is an update
                 event_name = 'content_updated'
                 logger.info(f"ContentInstance {instance.id} updated, triggering webhook.")
        except ContentInstance.DoesNotExist:
             pass # Should not happen

    if event_name:
        # Prepare payload (customize as needed)
        payload = {
            'content_instance_id': str(instance.id),
            'content_type_api_id': instance.content_type.api_id,
            'status': instance.status,
            'updated_at': instance.updated_at.isoformat(),
            # Include basic field data? Be careful about size/sensitivity
        }
        trigger_webhooks_for_event.delay(event_name, payload)


@receiver(post_delete, sender=ContentInstance)
def content_instance_post_delete_handler(sender, instance, **kwargs):
    """Trigger webhook for content deletion."""
    event_name = 'content_deleted'
    logger.info(f"ContentInstance {instance.id} deleted, triggering webhook.")
    payload = {
        'content_instance_id': str(instance.id),
        'content_type_api_id': instance.content_type.api_id,
    }
    trigger_webhooks_for_event.delay(event_name, payload)


# --- MediaAsset Signals ---

@receiver(post_save, sender=MediaAsset)
def media_asset_post_save_handler(sender, instance, created, **kwargs):
    """Trigger webhook for media upload/update."""
    if created:
        event_name = 'media_uploaded'
        logger.info(f"MediaAsset {instance.id} uploaded, triggering webhook.")
        payload = {
            'media_asset_id': str(instance.id),
            'filename': instance.filename,
            'mime_type': instance.mime_type,
            'size': instance.size,
            'uploader_id': str(instance.uploader_id) if instance.uploader_id else None,
        }
        trigger_webhooks_for_event.delay(event_name, payload)
    # else:
        # Trigger 'media_updated' if metadata changes? Might be too noisy.
        # pass


@receiver(post_delete, sender=MediaAsset)
def media_asset_post_delete_handler(sender, instance, **kwargs):
    """Trigger webhook for media deletion."""
    event_name = 'media_deleted'
    logger.info(f"MediaAsset {instance.id} deleted, triggering webhook.")
    payload = {
        'media_asset_id': str(instance.id),
        'filename': instance.filename,
    }
    trigger_webhooks_for_event.delay(event_name, payload)


# Note: Need to connect signals in apps.webhooks.apps.WebhooksConfig ready() method
# OR connect them within the ready() methods of the apps where the models reside (content, media).
# Connecting within the originating app is often preferred.