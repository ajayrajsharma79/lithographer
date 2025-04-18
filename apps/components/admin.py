from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ComponentDefinition, ComponentFieldDefinition # PageComponent managed inline

# Inline admin for Component Field Definitions
class ComponentFieldDefinitionInline(admin.TabularInline):
    model = ComponentFieldDefinition
    extra = 1
    ordering = ('order',)
    fields = ('name', 'api_id', 'field_type', 'order', 'config')
    prepopulated_fields = {"api_id": ("name",)}
    # TODO: Consider custom widget for 'config' JSON field


@admin.register(ComponentDefinition)
class ComponentDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for ComponentDefinition."""
    list_display = ('name', 'api_id', 'description', 'field_count')
    search_fields = ('name', 'api_id', 'description')
    inlines = [ComponentFieldDefinitionInline]
    prepopulated_fields = {"api_id": ("name",)}

    def field_count(self, obj):
        return obj.field_definitions.count()
    field_count.short_description = _("Fields")

# Note: PageComponent is intended to be managed via an inline
# within the ContentInstanceAdmin for relevant ContentTypes (e.g., 'Page').
# This requires modifying ContentInstanceAdmin in apps/content/admin.py.
