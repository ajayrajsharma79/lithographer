from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    ContentType, FieldDefinition, Taxonomy, Term,
    ContentInstance, ContentFieldInstance, ContentVersion
)
# Import component models for inline
from apps.components.models import PageComponent

# Inline admin for Field Definitions within Content Type
class FieldDefinitionInline(admin.TabularInline):
    model = FieldDefinition
    extra = 1 # Number of empty forms to display
    ordering = ('order',)
    fields = ('name', 'api_id', 'field_type', 'order', 'config')
    # Make config field wider if needed using formfield_overrides
    # formfield_overrides = {
    #     models.JSONField: {'widget': JSONEditorWidget}, # Requires django-jsoneditor or similar
    # }
    prepopulated_fields = {"api_id": ("name",)}


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    """Admin configuration for ContentType."""
    list_display = ('name', 'api_id', 'description', 'field_count', 'updated_at')
    search_fields = ('name', 'api_id', 'description')
    inlines = [FieldDefinitionInline]
    prepopulated_fields = {"api_id": ("name",)}

    def field_count(self, obj):
        return obj.field_definitions.count()
    field_count.short_description = _("Fields")


# Inline admin for Term Translations (Example - needs refinement)
# class TermTranslationInline(admin.TabularInline):
#     # This requires a separate model for translations or complex widget handling
#     # For now, we rely on editing the JSON fields directly.
#     model = Term # Placeholder - needs adjustment
#     extra = 1

@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    """Admin configuration for Taxonomy."""
    list_display = ('name', 'api_id', 'hierarchical', 'content_type_list')
    search_fields = ('name', 'api_id')
    filter_horizontal = ('content_types',) # Better widget for M2M
    prepopulated_fields = {"api_id": ("name",)}

    def content_type_list(self, obj):
        return ", ".join([ct.name for ct in obj.content_types.all()])
    content_type_list.short_description = _("Applicable Content Types")


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """Admin configuration for Term."""
    list_display = ('__str__', 'taxonomy', 'parent', 'slug_list')
    list_filter = ('taxonomy',)
    search_fields = ('taxonomy__name', 'translated_names', 'translated_slugs') # Search JSON
    # Need custom form/widgets to handle JSON fields nicely, ideally showing
    # separate inputs for each active language.
    fields = ('taxonomy', 'parent', 'translated_names', 'translated_slugs')
    # Consider using django-mptt for efficient hierarchy management if needed
    # list_display = ('name', 'taxonomy', 'parent', 'slug') # If using MPTT fields

    def slug_list(self, obj):
        return ", ".join(obj.translated_slugs.values())
    slug_list.short_description = _("Slugs")


# --- Content Instance Admin (Needs Significant Customization) ---

# Inline for Content Field Instances - Complex!
# This basic inline won't work well due to dynamic fields and localization.
# A custom ModelAdmin with a dynamic form is required here.
class ContentFieldInstanceInline(admin.TabularInline):
    model = ContentFieldInstance
    extra = 0 # Don't show empty by default, form should be dynamic
    fields = ('field_definition', 'language', 'value')
    readonly_fields = ('field_definition',) # Definition shouldn't change here

    # This needs heavy customization to:
    # 1. Only show fields relevant to the parent ContentInstance's ContentType.
    # 2. Render the correct widget for 'value' based on field_definition.field_type.
    # 3. Handle 'language' field visibility based on field_definition.is_localizable.
    # 4. Potentially group fields by language.


# Inline for Page Components (Layout Builder)
class PageComponentInline(admin.StackedInline): # Stacked might be better for component forms
    model = PageComponent
    extra = 0
    fk_name = 'page'
    ordering = ('order',)
    # Define fields shown in the inline form
    fields = ('component_definition', 'data', 'order')
    # readonly_fields = ('component_definition',) # Allow changing component type? Maybe not.
    sortable_field_name = "order" # If using django-admin-sortable2

    # --- MAJOR CUSTOMIZATION NEEDED ---
    # This inline requires significant customization:
    # 1. JavaScript to handle drag-and-drop reordering (updating the 'order' field).
    #    Libraries like SortableJS or django-admin-sortable2 can help.
    # 2. Dynamic Form Generation: The 'data' field needs a custom widget/form
    #    that renders the correct input fields based on the selected
    #    'component_definition' and its 'field_definitions'. This likely involves
    #    JavaScript fetching field definitions and rendering inputs, then saving
    #    the structured data back to the JSON 'data' field.
    # 3. Potentially a more visual "Add Component" interface instead of the default
    #    Django inline "Add another" button.


@admin.register(ContentInstance)
class ContentInstanceAdmin(admin.ModelAdmin):
    """
    Admin configuration for ContentInstance.
    Requires significant customization for a usable editing experience.
    """
    list_display = ('__str__', 'content_type', 'status', 'author_email', 'updated_at', 'published_at')
    list_filter = ('status', 'content_type', 'author', 'published_at')
    search_fields = ('id', 'content_type__name', 'author__email') # Searching actual content requires joining ContentFieldInstance
    readonly_fields = ('created_at', 'updated_at', 'published_at', 'author') # Author set automatically
    # inlines = [] # Start with empty inlines

    # Define base fieldsets - dynamically add content fields / layout editor
    fieldsets = (
        (None, {'fields': ('content_type', 'status')}),
        (_('Metadata'), {'fields': ('author', 'created_at', 'updated_at', 'published_at')}),
        # ('Content Fields', {'fields': ()}), # Placeholder - Fields are added dynamically
        (_('Taxonomies'), {'fields': ('terms',)}),
        # NOTE: Multilingual content editing requires significant customization below
        # in get_form, save_related, and potentially render_change_form to present
        # localizable fields grouped by language (e.g., using tabs).
    )
    filter_horizontal = ('terms',)

    def save_model(self, request, obj, form, change):
        if not obj.pk: # If creating new instance
            obj.author = request.user
        super().save_model(request, obj, form, change)
        # TODO: Trigger ContentVersion creation here or via signals

    def get_queryset(self, request):
        # Prefetch related data for efficiency
        return super().get_queryset(request).select_related('content_type', 'author')

    def get_inline_instances(self, request, obj=None):
        """Conditionally show PageComponentInline for specific content types."""
        inline_instances = []
        # Define which content types use the layout builder
        layout_builder_types = ['page', 'landingpage'] # Example API IDs
        if obj and obj.content_type.api_id in layout_builder_types:
            inline_instances.append(PageComponentInline(self.model, self.admin_site))
        # else:
            # Potentially add ContentFieldInstanceInline here for non-page types
            # if needed, but requires heavy customization as noted above.
            # inline_instances.append(ContentFieldInstanceInline(self.model, self.admin_site))
        return inline_instances

    def get_fieldsets(self, request, obj=None):
         """Hide standard content fields if using layout builder?"""
         # Define which content types use the layout builder
         layout_builder_types = ['page', 'landingpage'] # Example API IDs
         if obj and obj.content_type.api_id in layout_builder_types:
             # For page types, maybe only show metadata and taxonomies,
             # as content is managed via PageComponents inline
             return (
                 (None, {'fields': ('content_type', 'status')}),
                 (_('Metadata'), {'fields': ('author', 'created_at', 'updated_at', 'published_at')}),
                 (_('Taxonomies'), {'fields': ('terms',)}),
             )
         else:
             # For standard content types, show the basic fieldsets
             # (Dynamic content fields still need custom form generation)
             return self.fieldsets # Return the default defined fieldsets

    def author_email(self, obj):
        return obj.author.email if obj.author else 'N/A'
    author_email.short_description = _('Author')

    # --- Methods needing override for dynamic form generation ---
    # def get_form(self, request, obj=None, **kwargs):
    #     # Dynamically generate form based on obj.content_type.field_definitions
    #     # Add fields for each FieldDefinition, handling localization
    #     pass

    # def save_related(self, request, form, formsets, change):
    #     # Handle saving data from dynamic fields into ContentFieldInstance objects
    #     super().save_related(request, form, formsets, change)
    #     # Custom logic to parse dynamic form data and create/update ContentFieldInstance
    #     pass

    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     # Modify context to support multilingual tabs/widgets if needed
    #     return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    """Admin configuration for ContentVersion (read-only)."""
    list_display = ('content_instance', 'created_at', 'created_by_email', 'status_snapshot', 'version_message')
    list_filter = ('content_instance__content_type', 'created_by', 'created_at')
    search_fields = ('content_instance__id', 'created_by__email', 'version_message', 'data_snapshot')
    readonly_fields = [f.name for f in ContentVersion._meta.fields] # Make all fields read-only
    list_select_related = ('content_instance', 'created_by')

    def created_by_email(self, obj):
        return obj.created_by.email if obj.created_by else 'N/A'
    created_by_email.short_description = _('Created By')

    def has_add_permission(self, request):
        return False # Versions created programmatically

    def has_change_permission(self, request, obj=None):
        return False # Versions are immutable snapshots

    def has_delete_permission(self, request, obj=None):
        # Allow deletion? Or keep history permanently?
        return super().has_delete_permission(request, obj)

# Note: ContentFieldInstance is not registered directly, managed via ContentInstanceAdmin
