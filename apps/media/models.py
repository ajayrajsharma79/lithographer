import uuid
import os
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.files.storage import default_storage

# Helper function for upload path
def get_media_asset_upload_path(instance, filename):
    # Basic upload path: media/<asset_uuid>/<filename>
    # Consider adding folder path if instance.folder is set
    folder_path = f"folder_{instance.folder.id}/" if instance.folder else "uncategorized/"
    # Sanitize filename?
    return os.path.join('media_assets', folder_path, str(instance.id), filename)

class Folder(models.Model):
    """Represents a folder in the Media Library for organization."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Folder Name"), max_length=255)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE, # Deleting parent deletes child folders
        null=True,
        blank=True,
        related_name='subfolders',
        verbose_name=_("Parent Folder")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Folder")
        verbose_name_plural = _("Folders")
        # Ensure name is unique within a parent folder
        unique_together = ('parent', 'name')
        ordering = ['name']

    def __str__(self):
        # Basic string representation, could be enhanced to show full path
        return self.name


class MediaTag(models.Model):
    """Represents a tag that can be applied to media assets."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Tag Name"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Media Tag")
        verbose_name_plural = _("Media Tags")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MediaAsset(models.Model):
    """Represents a single file asset in the Media Library."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Store translated title, alt_text, caption
    translated_title = models.JSONField(
        _("Translated Title"),
        default=dict, blank=True,
        help_text=_("Title in different languages (JSON: {'lang_code': 'Title'}). Falls back to filename if empty.")
    )
    translated_alt_text = models.JSONField(
        _("Translated Alt Text"),
        default=dict, blank=True,
        help_text=_("Alt text in different languages (JSON: {'lang_code': 'Alt Text'}). Important for accessibility.")
    )
    translated_caption = models.JSONField(
        _("Translated Caption"),
        default=dict, blank=True,
        help_text=_("Caption in different languages (JSON: {'lang_code': 'Caption'}).")
    )
    file = models.FileField(
        _("File"),
        upload_to=get_media_asset_upload_path,
        max_length=500 # Increased length for potentially long paths/UUIDs
    )
    # Store common metadata directly
    filename = models.CharField(_("Original Filename"), max_length=255, editable=False)
    mime_type = models.CharField(_("MIME Type"), max_length=100, editable=False, blank=True)
    size = models.PositiveIntegerField(_("File Size (bytes)"), editable=False, null=True)
    # Image specific fields (populated by signal/task)
    width = models.PositiveIntegerField(_("Width (px)"), null=True, blank=True, editable=False)
    height = models.PositiveIntegerField(_("Height (px)"), null=True, blank=True, editable=False)
    # User-editable metadata fields removed, replaced by JSON fields above

    # Organization & Relations
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL, # Keep asset if folder deleted, move to root?
        null=True,
        blank=True,
        related_name='assets',
        verbose_name=_("Folder")
    )
    tags = models.ManyToManyField(
        MediaTag,
        blank=True,
        related_name="assets",
        verbose_name=_("Tags")
    )
    # Custom metadata
    custom_metadata = models.JSONField(
        _("Custom Metadata"),
        default=dict,
        blank=True,
        help_text=_("Arbitrary key-value pairs for additional metadata.")
    )
    # Tracking
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True, # Might be uploaded by system/migration
        related_name='uploaded_media_assets',
        verbose_name=_("Uploader")
    )
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Track metadata updates

    # Store optimized versions info (e.g., URLs to different sizes/formats)
    # This could be generated by the optimization task
    optimized_versions = models.JSONField(
        _("Optimized Versions"),
        default=dict,
        blank=True,
        editable=False,
        help_text=_("Stores URLs/paths to different optimized versions (e.g., {'thumbnail': '...', 'webp': '...'}).")
    )

    class Meta:
        verbose_name = _("Media Asset")
        verbose_name_plural = _("Media Assets")
        ordering = ['-upload_timestamp']

    def __str__(self):
        # Use helper to get title in current language or fallback
        return self.get_title() or self.filename or str(self.id)

    def save(self, *args, **kwargs):
        if self.file and not self.filename:
            self.filename = os.path.basename(self.file.name)
        # MIME type, size, dimensions should ideally be set by a signal/task after upload
        super().save(*args, **kwargs)

    @property
    def file_url(self):
        """Returns the public URL for the file."""
        if self.file:
            try:
                return default_storage.url(self.file.name)
            except Exception:
                # Handle cases where URL generation might fail
                return None
        return None

    @property
    def is_image(self):
        """Check if the asset is likely an image based on MIME type."""
        return self.mime_type and self.mime_type.startswith('image/')

    # --- Helper methods for translated fields ---
    def _get_translated_field(self, field_data, language_code=None, fallback=True):
        """Helper to get value from a translated JSON field."""
        if language_code is None:
            language_code = settings.LANGUAGE_CODE

        value = field_data.get(language_code)
        if value is None and fallback:
            # Fallback 1: Base language (e.g., 'en' from 'en-us')
            base_language = language_code.split('-')[0]
            value = field_data.get(base_language)
            # Fallback 2: Site default language
            if value is None and settings.LANGUAGE_CODE != base_language:
                 value = field_data.get(settings.LANGUAGE_CODE)
            # Fallback 3: First available language
            if value is None and field_data:
                 value = next(iter(field_data.values()), None)
        return value or "" # Return empty string if no value found

    def get_title(self, language_code=None, fallback=True):
        return self._get_translated_field(self.translated_title, language_code, fallback)

    def get_alt_text(self, language_code=None, fallback=True):
        return self._get_translated_field(self.translated_alt_text, language_code, fallback)

    def get_caption(self, language_code=None, fallback=True):
        return self._get_translated_field(self.translated_caption, language_code, fallback)


class ImageOptimizationProfile(models.Model):
    """Defines settings for generating optimized image versions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Profile Name"), max_length=100, unique=True, help_text=_("e.g., 'Thumbnail', 'WebP Medium'"))
    width = models.PositiveIntegerField(_("Max Width (px)"), null=True, blank=True)
    height = models.PositiveIntegerField(_("Max Height (px)"), null=True, blank=True)
    format = models.CharField(
        _("Output Format"), max_length=10, blank=True,
        choices=[('JPEG', 'JPEG'), ('PNG', 'PNG'), ('WEBP', 'WebP'), ('AVIF', 'AVIF')],
        help_text=_("Leave blank to keep original format.")
    )
    quality = models.PositiveIntegerField(
        _("Quality (1-100)"), null=True, blank=True,
        help_text=_("Applicable to JPEG, WebP, AVIF. Leave blank for default.")
    )
    # Add other options like 'crop', 'upscale', etc. if needed
    is_active = models.BooleanField(_("Active"), default=True, help_text=_("Whether this profile should be applied automatically."))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Image Optimization Profile")
        verbose_name_plural = _("Image Optimization Profiles")
        ordering = ['name']

    def __str__(self):
        return self.name

# Optional: MediaVersion model
# class MediaVersion(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     asset = models.ForeignKey(MediaAsset, on_delete=models.CASCADE, related_name='versions')
#     # Store previous file path/reference, metadata snapshot, timestamp, user etc.
#     ...
