from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

from .models import Comment, STATUS_APPROVED, STATUS_REJECTED, STATUS_SPAM, STATUS_PENDING

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comments, focused on moderation."""
    list_display = ('user_link', 'content_link', 'short_body', 'status', 'submission_timestamp', 'parent_link')
    list_filter = ('status', 'submission_timestamp', 'content_instance__content_type') # Filter by status, date, content type
    search_fields = ('body', 'user__username', 'user__email', 'content_instance__id') # Search comment body, user, content ID
    list_editable = ('status',) # Allow quick status changes from list view
    list_per_page = 50
    ordering = ('-submission_timestamp',) # Show newest first for moderation
    readonly_fields = ('user', 'content_instance', 'parent', 'submission_timestamp') # These shouldn't be changed

    fieldsets = (
        (_('Comment Info'), {'fields': ('user_link', 'content_link', 'parent_link', 'submission_timestamp')}),
        (_('Moderation'), {'fields': ('status', 'body')}), # Allow editing body and status
    )

    # Custom actions for moderation
    actions = ['approve_comments', 'reject_comments', 'mark_as_spam']

    def get_queryset(self, request):
        # Optimize query
        return super().get_queryset(request).select_related('user', 'content_instance', 'parent', 'content_instance__content_type')

    # Display methods for links and truncated body
    def user_link(self, obj):
        if obj.user:
            # Assuming you have an admin change view for FrontEndUser
            link = reverse("admin:frontend_users_frontenduser_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', link, obj.user.username)
        return "N/A"
    user_link.short_description = _("User")
    user_link.admin_order_field = 'user__username'

    def content_link(self, obj):
        # Link to the ContentInstance admin change view
        link = reverse("admin:content_contentinstance_change", args=[obj.content_instance.pk])
        # Try to get a meaningful string representation of the content instance
        content_str = str(obj.content_instance)
        return format_html('<a href="{}">{}</a>', link, content_str)
    content_link.short_description = _("Content")
    content_link.admin_order_field = 'content_instance' # Basic ordering

    def parent_link(self, obj):
        if obj.parent:
            link = reverse("admin:comments_comment_change", args=[obj.parent.pk])
            return format_html('<a href="{}">{}</a>', link, obj.parent.pk)
        return "–" # Em dash for empty
    parent_link.short_description = _("In Reply To")

    def short_body(self, obj):
        return (obj.body[:75] + '...') if len(obj.body) > 75 else obj.body
    short_body.short_description = _("Comment (excerpt)")

    # Admin Actions
    def approve_comments(self, request, queryset):
        updated = queryset.update(status=STATUS_APPROVED)
        self.message_user(request, _(f"{updated} comments were successfully approved."))
        # TODO: Trigger 'comment_approved' webhook event here or via signal
    approve_comments.short_description = _("Approve selected comments")

    def reject_comments(self, request, queryset):
        updated = queryset.update(status=STATUS_REJECTED)
        self.message_user(request, _(f"{updated} comments were successfully rejected."))
    reject_comments.short_description = _("Reject selected comments")

    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status=STATUS_SPAM)
        self.message_user(request, _(f"{updated} comments were successfully marked as spam."))
    mark_as_spam.short_description = _("Mark selected comments as spam")

    # Override readonly_fields for the change view to make 'body' editable
    def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            return self.readonly_fields + ('user_link', 'content_link', 'parent_link')
        return self.readonly_fields

    def get_fieldsets(self, request, obj=None):
         # Customize fieldsets slightly for add vs change if needed, but keep simple for now
         return self.fieldsets

    # Disable adding comments directly via admin
    def has_add_permission(self, request):
        return False
