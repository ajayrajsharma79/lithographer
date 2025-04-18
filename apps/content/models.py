import uuid
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone # Import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify

# Import Language model from core app
from apps.core.models import Language

# Choices for FieldDefinition.field_type
FIELD_TYPE_CHOICES = [
    ('text', _('Text (Single Line)')),
    ('rich_text', _('Rich Text (Multi Line)')),
    ('number', _('Number (Integer/Float)')),
    ('date', _('Date/DateTime')),
    ('boolean', _('Boolean (True/False)')),
    ('email', _('Email Address')),
    ('url', _('URL')),
    ('media', _('Media (Link to Media Library)')), # Assumes a future Media model
    ('relationship', _('Relationship (Link to other Content Instance)')),
    ('select', _('Select (Dropdown/Radio)')),
    ('structured_list', _('Structured List (Repeater)')),
    ('json', _('JSON')),
]

# Choices for ContentInstance.status
STATUS_DRAFT = 'draft'
STATUS_IN_REVIEW = 'in_review'
STATUS_PUBLISHED = 'published'
STATUS_REJECTED = 'rejected'
STATUS_ARCHIVED = 'archived' # Added archived status
STATUS_CHOICES = [
    (STATUS_DRAFT, _('Draft')),
    (STATUS_IN_REVIEW, _('In Review')),
    (STATUS_PUBLISHED, _('Published')),
    (STATUS_REJECTED, _('Rejected')),
    (STATUS_ARCHIVED, _('Archived')),
]


class ContentType(models.Model):
    """
    Defines the structure (schema) for a type of content.
    e.g., Blog Post, Product, Page
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        _("Content Type Name"),
        max_length=100,
        unique=True,
        help_text=_("Human-readable name (e.g., 'Blog Post').")
    )
    api_id = models.SlugField(
        _("API ID"),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier used in APIs and code (e.g., 'blog_post'). Automatically generated if left blank.")
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Optional description of this content type.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Content Type")
        verbose_name_plural = _("Content Types")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.api_id = slugify(self.name)
        # Ensure api_id is unique
        if ContentType.objects.filter(api_id=self.api_id).exclude(pk=self.pk).exists():
             # Append suffix if collision occurs (simple approach)
             counter = 1
             original_api_id = self.api_id
             while ContentType.objects.filter(api_id=self.api_id).exclude(pk=self.pk).exists():
                 self.api_id = f"{original_api_id}-{counter}"
                 counter += 1
        super().save(*args, **kwargs)


class FieldDefinition(models.Model):
    """
    Defines a specific field within a ContentType.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='field_definitions',
        verbose_name=_("Content Type")
    )
    name = models.CharField(
        _("Field Name"),
        max_length=100,
        help_text=_("Human-readable name for the field (e.g., 'Post Title').")
    )
    api_id = models.SlugField(
        _("API ID"),
        max_length=100,
        help_text=_("Unique identifier for the field within the Content Type (e.g., 'post_title'). Automatically generated if left blank.")
    )
    field_type = models.CharField(
        _("Field Type"),
        max_length=50,
        choices=FIELD_TYPE_CHOICES,
        help_text=_("Determines the kind of data stored and the input widget used.")
    )
    order = models.PositiveIntegerField(
        _("Order"),
        default=0,
        help_text=_("Order in which fields appear in the admin interface.")
    )
    # Configuration stored as JSON for flexibility
    config = models.JSONField(
        _("Configuration"),
        default=dict,
        blank=True,
        help_text=_(
            "Field-specific settings (JSON format). Keys include: "
            "'required' (bool), 'unique' (bool, requires careful implementation), "
            "'default_value', 'help_text' (str), 'validation_rules' (e.g., min_length, max_length, regex), "
            "'localizable' (bool), 'select_options' (list for 'select' type), "
            "'allowed_content_types' (list of api_ids for 'relationship' type), "
            "'allowed_media_types' (list for 'media' type)."
        )
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Field Definition")
        verbose_name_plural = _("Field Definitions")
        ordering = ['content_type', 'order', 'name']
        # Ensure api_id is unique within a ContentType
        unique_together = ('content_type', 'api_id')

    def __str__(self):
        return f"{self.content_type.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.api_id = slugify(self.name)
        # Ensure api_id is unique within the content type
        if FieldDefinition.objects.filter(content_type=self.content_type, api_id=self.api_id).exclude(pk=self.pk).exists():
             counter = 1
             original_api_id = self.api_id
             while FieldDefinition.objects.filter(content_type=self.content_type, api_id=self.api_id).exclude(pk=self.pk).exists():
                 self.api_id = f"{original_api_id}-{counter}"
                 counter += 1
        super().save(*args, **kwargs)

    @property
    def is_localizable(self):
        return self.config.get('localizable', False)

    @property
    def is_required(self):
        return self.config.get('required', False)

    # Add more property accessors for config flags as needed


class Taxonomy(models.Model):
    """
    Defines a classification system (e.g., Categories, Tags).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        _("Taxonomy Name"),
        max_length=100,
        unique=True,
        help_text=_("Human-readable name (e.g., 'Categories').")
    )
    api_id = models.SlugField(
        _("API ID"),
        max_length=100,
        unique=True,
        help_text=_("Unique identifier for API use (e.g., 'categories'). Automatically generated.")
    )
    hierarchical = models.BooleanField(
        _("Hierarchical"),
        default=False,
        help_text=_("Does this taxonomy support parent-child relationships (like categories)?")
    )
    # Link Taxonomies to the ContentTypes they can be applied to
    content_types = models.ManyToManyField(
        ContentType,
        blank=True,
        related_name="taxonomies",
        verbose_name=_("Applicable Content Types"),
        help_text=_("Content types that can use this taxonomy.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Taxonomy")
        verbose_name_plural = _("Taxonomies")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.api_id:
            self.api_id = slugify(self.name)
        # Ensure api_id is unique
        if Taxonomy.objects.filter(api_id=self.api_id).exclude(pk=self.pk).exists():
             counter = 1
             original_api_id = self.api_id
             while Taxonomy.objects.filter(api_id=self.api_id).exclude(pk=self.pk).exists():
                 self.api_id = f"{original_api_id}-{counter}"
                 counter += 1
        super().save(*args, **kwargs)


class Term(models.Model):
    """
    Represents a single term within a Taxonomy (e.g., 'Technology' in 'Categories').
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    taxonomy = models.ForeignKey(
        Taxonomy,
        on_delete=models.CASCADE,
        related_name='terms',
        verbose_name=_("Taxonomy")
    )
    # Store translated names and slugs in JSON fields
    # Example: {"en": "Technology", "fr": "Technologie"}
    translated_names = models.JSONField(
        _("Translated Names"),
        default=dict,
        help_text=_("Term names in different languages (JSON format: {'lang_code': 'Name'}).")
    )
    # Example: {"en": "technology", "fr": "technologie"}
    translated_slugs = models.JSONField(
        _("Translated Slugs"),
        default=dict,
        help_text=_("Term slugs in different languages (JSON format: {'lang_code': 'slug'}).")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL, # Or models.CASCADE if children should be deleted
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Parent Term"),
        help_text=_("Used for hierarchical taxonomies.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Term")
        verbose_name_plural = _("Terms")
        ordering = ['taxonomy', 'translated_names'] # Order by default name? Needs refinement.
        # Ensure slug is unique within a language and taxonomy? Complex validation needed.

    def __str__(self):
        # Return name in default language or first available
        default_lang = settings.LANGUAGE_CODE
        return self.translated_names.get(default_lang, next(iter(self.translated_names.values()), str(self.id)))

    def clean(self):
        # Validate parent assignment based on taxonomy hierarchy
        if self.parent and not self.taxonomy.hierarchical:
            raise ValidationError(_("Cannot assign parent to a term in a non-hierarchical taxonomy."))
        if self.parent and self.parent.taxonomy != self.taxonomy:
            raise ValidationError(_("Parent term must belong to the same taxonomy."))
        # Add validation for unique slugs per language within taxonomy if needed

    def save(self, *args, **kwargs):
        # Auto-generate slugs from names if not provided
        for lang_code, name in self.translated_names.items():
            if lang_code not in self.translated_slugs or not self.translated_slugs[lang_code]:
                self.translated_slugs[lang_code] = slugify(name)
        super().save(*args, **kwargs)

    def get_name(self, language_code=None):
        """Helper to get name in a specific language or fallback."""
        if language_code is None:
            language_code = settings.LANGUAGE_CODE
        return self.translated_names.get(language_code, self.__str__()) # Fallback to default string

    def get_slug(self, language_code=None):
        """Helper to get slug in a specific language or fallback."""
        if language_code is None:
            language_code = settings.LANGUAGE_CODE
        return self.translated_slugs.get(language_code, slugify(self.get_name(language_code)))


class ContentInstance(models.Model):
    """
    Represents a single piece of content created based on a ContentType.
    e.g., A specific blog post, a particular product page.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT, # Prevent deleting ContentType if instances exist
        related_name='instances',
        verbose_name=_("Content Type")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Link to CMSUser
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='content_instances',
        verbose_name=_("Author")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField( # Track when first published
        _("Published At"),
        null=True, blank=True, db_index=True
    )
    # M2M relationship to Taxonomy Terms
    terms = models.ManyToManyField(
        Term,
        blank=True,
        related_name="content_instances",
        verbose_name=_("Taxonomy Terms"),
        help_text=_("Terms associated with this content instance.")
    )

    class Meta:
        verbose_name = _("Content Instance")
        verbose_name_plural = _("Content Instances")
        ordering = ['-updated_at']

    def __str__(self):
        # Try to find a representative field (e.g., 'title', 'name') for display
        # This requires querying ContentFieldInstance, might be slow for admin list display
        # A simpler default:
        return f"{self.content_type.name} Instance ({self.id})"

    def save(self, *args, **kwargs):
        # Set published_at timestamp when status changes to published
        if self.status == STATUS_PUBLISHED and self.published_at is None:
             # Check if it was already published before to avoid resetting
             try:
                 orig = ContentInstance.objects.get(pk=self.pk)
                 if orig.status != STATUS_PUBLISHED:
                     self.published_at = timezone.now()
             except ContentInstance.DoesNotExist:
                 self.published_at = timezone.now() # New instance being published
        super().save(*args, **kwargs)
        # Consider triggering version save here or via signals


class ContentFieldInstance(models.Model):
    """
    Stores the actual data for a specific field in a ContentInstance,
    potentially for a specific language.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_instance = models.ForeignKey(
        ContentInstance,
        on_delete=models.CASCADE,
        related_name='field_instances',
        verbose_name=_("Content Instance")
    )
    field_definition = models.ForeignKey(
        FieldDefinition,
        on_delete=models.CASCADE, # If field def is deleted, data is lost
        related_name='+', # No reverse relation needed from FieldDefinition
        verbose_name=_("Field Definition")
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        null=True, # Allow NULL for non-localizable fields
        blank=True,
        related_name='+', # No reverse relation needed from Language
        verbose_name=_("Language"),
        help_text=_("Language for this field value (null if field is not localizable).")
    )
    # Store the actual value in a flexible JSON field
    # This simplifies the model but requires careful handling/validation based on field_type
    # Alternatives: Separate value fields (value_text, value_int, etc.) or EAV pattern.
    value = models.JSONField(
        _("Value"),
        null=True, blank=True, # Allow null/empty values depending on field config
        help_text=_("The actual data stored for this field instance.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Content Field Instance")
        verbose_name_plural = _("Content Field Instances")
        ordering = ['content_instance', 'field_definition__order']
        # Ensure uniqueness for a given instance, field, and language
        unique_together = ('content_instance', 'field_definition', 'language')
        indexes = [
            models.Index(fields=['content_instance', 'field_definition', 'language']),
            # Add index on 'value' if specific JSON lookups are common and DB supports it
        ]

    def __str__(self):
        lang_code = f" ({self.language.code})" if self.language else ""
        return f"{self.content_instance} - {self.field_definition.name}{lang_code}"

    def clean(self):
        # Validate language requirement based on field definition
        if self.field_definition.is_localizable and self.language is None:
            raise ValidationError(_("Language is required for this localizable field."))
        if not self.field_definition.is_localizable and self.language is not None:
            raise ValidationError(_("Language must be null for non-localizable fields."))
        # Add validation for the 'value' based on field_definition.field_type
        # This requires more complex logic (e.g., check if value is int for 'number' type)
        # This validation is better handled in forms/serializers or model save method.

    # Add methods to get/set typed values from JSON if needed


class ContentVersion(models.Model):
    """
    Stores a historical snapshot of a ContentInstance's data.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_instance = models.ForeignKey(
        ContentInstance,
        on_delete=models.CASCADE, # Delete versions if instance is deleted
        related_name='versions',
        verbose_name=_("Content Instance")
    )
    # Store a snapshot of the relevant field data at the time of versioning
    # Structure: {"lang_code": {"field_api_id": value, ...}, "non_localizable": {"field_api_id": value, ...}}
    data_snapshot = models.JSONField(
        _("Data Snapshot"),
        help_text=_("Snapshot of content field instance data for this version.")
    )
    status_snapshot = models.CharField( # Store status at time of versioning
        _("Status Snapshot"),
        max_length=20,
        choices=STATUS_CHOICES
    )
    version_message = models.TextField(
        _("Version Message"),
        blank=True,
        help_text=_("Optional message describing the changes in this version.")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+', # No reverse needed
        verbose_name=_("Created By")
    )
    created_at = models.DateTimeField(
        _("Version Created At"),
        default=timezone.now # Use timezone.now for default
    )

    class Meta:
        verbose_name = _("Content Version")
        verbose_name_plural = _("Content Versions")
        ordering = ['content_instance', '-created_at']
        indexes = [
            models.Index(fields=['content_instance', '-created_at']),
        ]

    def __str__(self):
        return f"Version of {self.content_instance} at {self.created_at}"

    @staticmethod
    def create_version(content_instance, user=None, message=""):
        """Creates a new version snapshot for the given ContentInstance."""
        snapshot = {'non_localizable': {}}
        field_instances = content_instance.field_instances.select_related('field_definition', 'language').all()

        for fi in field_instances:
            fd_api_id = fi.field_definition.api_id
            if fi.language:
                lang_code = fi.language.code
                if lang_code not in snapshot:
                    snapshot[lang_code] = {}
                snapshot[lang_code][fd_api_id] = fi.value
            else:
                # Should only happen if field is not localizable
                snapshot['non_localizable'][fd_api_id] = fi.value

        version = ContentVersion.objects.create(
            content_instance=content_instance,
            data_snapshot=snapshot,
            status_snapshot=content_instance.status,
            created_by=user,
            version_message=message
        )
        return version

# Utility function to get the actual value storage field based on type
# (Not needed if using single JSON 'value' field)
# def get_value_field_name(field_type):
#     if field_type == 'text': return 'value_text'
#     # ... etc ...
