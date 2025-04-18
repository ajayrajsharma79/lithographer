import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# Import related models carefully to avoid circular dependencies if possible
# It's generally safe to import from other apps' models.py
from apps.content.models import ContentInstance
# Assuming FrontEndUser is the correct user type for comments
# If CMSUsers can also comment, adjust the FK accordingly or use a generic relation
from apps.frontend_users.models import FrontEndUser

# Comment Status Choices
STATUS_PENDING = 'pending'
STATUS_APPROVED = 'approved'
STATUS_REJECTED = 'rejected'
STATUS_SPAM = 'spam'
COMMENT_STATUS_CHOICES = [
    (STATUS_PENDING, _('Pending')),
    (STATUS_APPROVED, _('Approved')),
    (STATUS_REJECTED, _('Rejected')),
    (STATUS_SPAM, _('Spam')),
]

class Comment(models.Model):
    """Represents a comment on a ContentInstance."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_instance = models.ForeignKey(
        ContentInstance,
        on_delete=models.CASCADE, # Delete comments if content is deleted
        related_name='comments',
        verbose_name=_("Content Instance")
    )
    user = models.ForeignKey(
        FrontEndUser, # Link to the front-end user who made the comment
        on_delete=models.CASCADE, # Delete comments if user is deleted
        related_name='comments',
        verbose_name=_("User")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, # Delete replies if parent is deleted
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_("Parent Comment"),
        help_text=_("Used for threaded comments.")
    )
    body = models.TextField(_("Comment Body"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=COMMENT_STATUS_CHOICES,
        default=STATUS_PENDING, # Comments require moderation by default
        db_index=True
    )
    submission_timestamp = models.DateTimeField(_("Submitted At"), default=timezone.now)
    # Optional: Add fields like 'ip_address', 'user_agent' for moderation purposes

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['submission_timestamp'] # Order chronologically by default

    def __str__(self):
        return f"Comment by {self.user} on {self.content_instance}"

    @property
    def is_approved(self):
        return self.status == STATUS_APPROVED

    # Consider adding methods for easy moderation state changes if needed
    # def approve(self): ...
    # def reject(self): ...
