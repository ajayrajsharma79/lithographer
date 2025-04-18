from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import WebhookEndpoint, WebhookEventLog

@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(admin.ModelAdmin):
    """Admin configuration for the WebhookEndpoint model."""
    list_display = ('target_url', 'get_event_summary', 'is_active', 'created_by_email', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('target_url', 'created_by__email', 'subscribed_events') # Search JSONField might need DB specific setup
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'secret_display') # Don't show full secret
    raw_id_fields = ('created_by',) # Use simpler widget for user FK

    fieldsets = (
        (None, {'fields': ('target_url', 'subscribed_events', 'is_active')}),
        (_('Security'), {'fields': ('secret',)}), # Use 'secret' for input
        (_('Metadata'), {'fields': ('created_by', 'created_at', 'updated_at')}),
    )

    # Use 'secret' field for input, but don't display existing secret
    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = super().get_fieldsets(request, obj)
    #     # Modify fieldsets based on obj existence if needed
    #     return fieldsets

    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(super().get_readonly_fields(request, obj))
        # Make secret readonly if object exists, otherwise it's for input
        # However, showing even a masked secret might be undesirable.
        # Best practice is often to make it write-only after creation.
        # For simplicity here, we allow editing but don't display the saved value.
        # if obj:
        #     if 'secret' not in ro_fields:
        #         ro_fields.append('secret') # Make existing secret uneditable
        return tuple(ro_fields)


    def created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else 'N/A'
    created_by_email.short_description = _('Created By')
    created_by_email.admin_order_field = 'created_by__email'

    def get_event_summary(self, obj):
        """Provide a summary of subscribed events."""
        events = obj.subscribed_events
        if not events:
            return "None"
        if "*" in events:
            return "All Events (*)"
        count = len(events)
        return f"{count} event(s): {', '.join(events[:3])}{'...' if count > 3 else ''}"
    get_event_summary.short_description = _('Subscribed Events')

    # Add a field to display that a secret is set, without showing it
    def secret_display(self, obj):
        return "Set" if obj.secret else "Not Set"
    secret_display.short_description = _('Secret Status')


@admin.register(WebhookEventLog)
class WebhookEventLogAdmin(admin.ModelAdmin):
    """Admin configuration for the WebhookEventLog model (read-only)."""
    list_display = ('timestamp', 'endpoint_url', 'event_type', 'status', 'response_status_code', 'is_successful')
    list_filter = ('status', 'event_type', 'timestamp', 'endpoint')
    search_fields = ('endpoint__target_url', 'event_type', 'payload', 'response_body') # Searching JSON/Text fields
    ordering = ('-timestamp',)
    readonly_fields = [f.name for f in WebhookEventLog._meta.fields] # Make all fields read-only

    list_select_related = ('endpoint',) # Optimize query for endpoint URL

    def endpoint_url(self, obj):
        return obj.endpoint.target_url
    endpoint_url.short_description = _('Endpoint URL')
    endpoint_url.admin_order_field = 'endpoint__target_url'

    # Disable add, change, delete permissions for logs via admin
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
