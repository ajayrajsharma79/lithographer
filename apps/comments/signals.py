import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, STATUS_PENDING, STATUS_APPROVED
# Import the trigger task carefully to avoid circular imports if tasks import models
# from apps.webhooks.tasks import trigger_webhooks_for_event

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Comment)
def comment_post_save_handler(sender, instance, created, **kwargs):
    """
    Handle actions after a comment is saved.
    Trigger webhooks for 'comment_submitted' or 'comment_approved'.
    """
    # Import task here to avoid potential circular dependency at module level
    from apps.webhooks.tasks import trigger_webhooks_for_event

    event_name = None
    if created and instance.status == STATUS_PENDING:
        event_name = 'comment_submitted'
        logger.info(f"Comment {instance.id} submitted, triggering webhook.")
    elif not created:
        # Check if status changed to approved
        try:
            # Get the previous state if possible (requires tracking or querying DB)
            # This is a simplified check assuming status was different before save
            if instance.status == STATUS_APPROVED:
                 # More robust check: query previous state or use django-dirtyfields
                 # For now, assume any save resulting in APPROVED triggers it
                 event_name = 'comment_approved'
                 logger.info(f"Comment {instance.id} approved, triggering webhook.")
        except Comment.DoesNotExist:
             # Should not happen in post_save unless instance deleted concurrently
             pass

    if event_name:
        # Prepare payload (customize as needed)
        payload = {
            'comment_id': str(instance.id),
            'content_instance_id': str(instance.content_instance_id),
            'user_id': str(instance.user_id),
            'status': instance.status,
            'body_excerpt': instance.body[:100] + ('...' if len(instance.body) > 100 else ''),
            'submission_timestamp': instance.submission_timestamp.isoformat(),
        }
        trigger_webhooks_for_event.delay(event_name, payload)

# Note: Need to connect signals in apps.comments.apps.CommentsConfig ready() method