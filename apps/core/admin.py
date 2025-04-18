from django.contrib import admin
from .models import Language, SystemSetting

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin configuration for the Language model."""
    list_display = ('name', 'code', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'code')
    ordering = ('name',)
    # Prevent making multiple languages default via admin save
    readonly_fields = ('is_default',) # is_default is managed by model logic and LanguageViewSet action

    # Optional: Action to set default language (alternative to ViewSet action)
    # def set_as_default(self, request, queryset):
    #     if queryset.count() != 1:
    #         self.message_user(request, "Please select exactly one language to set as default.", level='warning')
    #         return
    #     language = queryset.first()
    #     if not language.is_active:
    #          self.message_user(request, "Cannot set an inactive language as default.", level='error')
    #          return
    #     language.is_default = True
    #     language.save()
    #     # Update SystemSetting as well
    #     system_settings = SystemSetting.load()
    #     if system_settings.default_language != language:
    #         system_settings.default_language = language
    #         system_settings.save(update_fields=['default_language'])
    #     self.message_user(request, f"'{language.name}' set as default language.", level='success')
    # set_as_default.short_description = "Set selected language as default"
    # actions = [set_as_default]


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """Admin configuration for the SystemSetting singleton model."""
    list_display = ('site_name', 'get_default_language_display', 'timezone')
    # Prevent adding more than one instance via the admin
    def has_add_permission(self, request):
        return not SystemSetting.objects.exists()

    # Prevent deleting the single instance
    def has_delete_permission(self, request, obj=None):
        return False

    # Customize fieldsets for better layout
    fieldsets = (
        (None, {
            'fields': ('site_name', 'default_language', 'timezone')
        }),
        # Add other setting groups here
    )

    def get_default_language_display(self, obj):
        return obj.default_language if obj.default_language else "Not Set"
    get_default_language_display.short_description = 'Default Language'

    # Ensure the object always exists when accessing the change page
    def changelist_view(self, request, extra_context=None):
        SystemSetting.load() # Ensure the singleton exists
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # The object_id will always be '1' due to the singleton pattern
        SystemSetting.load() # Ensure the singleton exists
        return super().change_view(request, '1', form_url, extra_context)

    # Limit queryset to the single instance
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ensure the instance exists if accessed via admin
        SystemSetting.load()
        return qs.filter(pk=1)
