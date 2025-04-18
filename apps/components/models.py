import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# Import ContentInstance from content app
from apps.content.models import ContentInstance

# Reuse field type choices if possible, or define specific ones for components
from apps.content.models import FIELD_TYPE_CHOICES

class ComponentDefinition(models.Model):
    """
    Defines a reusable front-end component structure.
    e.g., Hero Banner, Call To Action, Image Gallery
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        _("Component Name"),
        max_length=100,
        unique=True,
        help_text=_("Human-readable name (e.g., 'Hero Banner').")
    )
    api_id = models.SlugField(
        _("API ID"),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier used in APIs and code (e.g., 'hero_banner'). Automatically generated.")
    )
    description = models.TextField(_("Description"), blank=True)
    # Optional: Field for icon class or preview image URL for admin UI
    icon = models.CharField(_("Icon Class/URL"), max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Component Definition")
        verbose_name_plural = _("Component Definitions")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.api_id = slugify(self.name)
        # Ensure api_id is unique
        if ComponentDefinition.objects.filter(api_id=self.api_id).exclude(pk=self.pk).exists():
             counter = 1
             original_api_id = self.api_id
             while ComponentDefinition.objects.filter(api_id=self.api_id).exclude(pk=self.pk).exists():
                 self.api_id = f"{original_api_id}-{counter}"
                 counter += 1
        super().save(*args, **kwargs)


class ComponentFieldDefinition(models.Model):
    """
    Defines a configurable field within a ComponentDefinition.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component_definition = models.ForeignKey(
        ComponentDefinition,
        on_delete=models.CASCADE,
        related_name='field_definitions',
        verbose_name=_("Component Definition")
    )
    name = models.CharField(
        _("Field Name"),
        max_length=100,
        help_text=_("Human-readable name for the field (e.g., 'Headline').")
    )
    api_id = models.SlugField(
        _("API ID"),
        max_length=100,
        help_text=_("Unique identifier for the field within the Component Definition (e.g., 'headline'). Automatically generated.")
    )
    field_type = models.CharField(
        _("Field Type"),
        max_length=50,
        choices=FIELD_TYPE_CHOICES, # Reuse choices from content app
        help_text=_("Determines the kind of data stored and the input widget used.")
    )
    order = models.PositiveIntegerField(
        _("Order"),
        default=0,
        help_text=_("Order in which fields appear in the component configuration form.")
    )
    config = models.JSONField(
        _("Configuration"),
        default=dict,
        blank=True,
        help_text=_(
            "Field-specific settings (JSON format). Keys include: "
            "'required' (bool), 'default_value', 'help_text' (str), "
            "'select_options' (list for 'select' type), "
            "'allowed_content_types' (list of api_ids for 'relationship' type), "
            "'allowed_media_types' (list for 'media' type)."
            # Note: 'localizable' is typically not needed here as component data is stored per page instance.
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Component Field Definition")
        verbose_name_plural = _("Component Field Definitions")
        ordering = ['component_definition', 'order', 'name']
        unique_together = ('component_definition', 'api_id')

    def __str__(self):
        return f"{self.component_definition.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.api_id = slugify(self.name)
        # Ensure api_id is unique within the component definition
        if ComponentFieldDefinition.objects.filter(component_definition=self.component_definition, api_id=self.api_id).exclude(pk=self.pk).exists():
             counter = 1
             original_api_id = self.api_id
             while ComponentFieldDefinition.objects.filter(component_definition=self.component_definition, api_id=self.api_id).exclude(pk=self.pk).exists():
                 self.api_id = f"{original_api_id}-{counter}"
                 counter += 1
        super().save(*args, **kwargs)


class PageComponent(models.Model):
    """
    Represents an instance of a ComponentDefinition placed on a specific Page (ContentInstance).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(
        ContentInstance,
        on_delete=models.CASCADE,
        related_name='components',
        verbose_name=_("Page"),
        limit_choices_to={'content_type__api_id__in': ['page', 'landingpage']}, # Example: Limit to specific content types
        help_text=_("The page this component instance belongs to.")
    )
    component_definition = models.ForeignKey(
        ComponentDefinition,
        on_delete=models.PROTECT, # Prevent deleting definition if used on pages
        related_name='instances',
        verbose_name=_("Component Definition")
    )
    order = models.PositiveIntegerField(
        _("Order"),
        default=0,
        db_index=True,
        help_text=_("Order of this component on the page.")
    )
    # Store configured data for this specific instance of the component
    data = models.JSONField(
        _("Component Data"),
        default=dict,
        blank=True,
        help_text=_("Stores the configured values for the component's fields, keyed by field API ID.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Page Component")
        verbose_name_plural = _("Page Components")
        ordering = ['page', 'order']
        indexes = [
            models.Index(fields=['page', 'order']),
        ]

    def __str__(self):
        return f"{self.component_definition.name} on Page {self.page_id} (Order: {self.order})"
