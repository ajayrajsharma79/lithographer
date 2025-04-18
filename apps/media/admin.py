from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from .models import Folder, MediaTag, MediaAsset, ImageOptimizationProfile

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    """Admin configuration for Folders."""
    list_display = ('name', 'parent', 'asset_count')
    search_fields = ('name',)
    list_filter = ('parent',) # Filter by parent folder
    # Consider using django-mptt for better hierarchy display/management

    def asset_count(self, obj):
        return obj.assets.count()
    asset_count.short_description = _("Assets")


@admin.register(MediaTag)
class MediaTagAdmin(admin.ModelAdmin):
    """Admin configuration for Media Tags."""
    list_display = ('name', 'slug', 'asset_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

    def asset_count(self, obj):
        return obj.assets.count()
    asset_count.short_description = _("Assets")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    """Admin configuration for Media Assets."""
    list_display = ('admin_thumbnail', 'title_or_filename', 'mime_type', 'size_display', 'folder', 'upload_timestamp', 'uploader_email')
    list_filter = ('mime_type', 'folder', 'upload_timestamp', 'tags')
    # Update search fields for JSON translation fields
    search_fields = ('translated_title', 'filename', 'translated_alt_text', 'translated_caption', 'custom_metadata', 'tags__name', 'uploader__email')
    readonly_fields = ('filename', 'mime_type', 'size', 'width', 'height', 'upload_timestamp', 'uploader', 'optimized_versions', 'file_url_display')
    filter_horizontal = ('tags',)
    list_select_related = ('folder', 'uploader') # Optimize queries

    fieldsets = (
        (None, {'fields': ('file', 'file_url_display')}), # File upload/display
        # Add translated fields - requires custom widget for good UX,
        # ideally showing separate inputs for each active language.
        (_('Translated Metadata'), {'fields': ('translated_title', 'translated_alt_text', 'translated_caption')}),
        (_('Other Metadata'), {'fields': ('tags', 'custom_metadata')}),
        (_('Organization'), {'fields': ('folder',)}),
        (_('File Info (Read-Only)'), {'fields': ('filename', 'mime_type', 'size_display', 'dimensions_display', 'upload_timestamp', 'uploader_email')}),
        (_('Optimized Versions (Read-Only)'), {'fields': ('optimized_versions',)}),
    )

    def title_or_filename(self, obj):
        # Use the helper method to get title in default language
        return obj.get_title() or obj.filename
    title_or_filename.short_description = _("Title/Filename")
    # title_or_filename.admin_order_field = 'title' # Cannot easily sort by JSON field value

    def size_display(self, obj):
        if obj.size is None:
            return "N/A"
        # Simple KB/MB formatting
        if obj.size < 1024 * 1024:
            return f"{obj.size / 1024:.1f} KB"
        else:
            return f"{obj.size / (1024 * 1024):.1f} MB"
    size_display.short_description = _("Size")
    size_display.admin_order_field = 'size'

    def dimensions_display(self, obj):
        if obj.width and obj.height:
            return f"{obj.width} x {obj.height} px"
        return "N/A"
    dimensions_display.short_description = _("Dimensions")

    def uploader_email(self, obj):
        return obj.uploader.email if obj.uploader else 'N/A'
    uploader_email.short_description = _('Uploader')
    uploader_email.admin_order_field = 'uploader__email'

    def admin_thumbnail(self, obj):
        if obj.is_image:
            # Use optimized thumbnail if available, otherwise original
            thumb_url = obj.optimized_versions.get('thumbnail', obj.file_url)
            if thumb_url:
                return format_html('<img src="{}" style="max-height: 50px; max-width: 80px;" />', thumb_url)
        # TODO: Add icons for non-image types
        return "N/A"
    admin_thumbnail.short_description = _("Thumbnail")

    def file_url_display(self, obj):
         url = obj.file_url
         if url:
             return format_html('<a href="{0}" target="_blank">{0}</a>', url)
         return "N/A"
    file_url_display.short_description = _("File URL")

    def save_model(self, request, obj, form, change):
        if not obj.pk: # If creating new instance
            obj.uploader = request.user
        # TODO: Trigger metadata extraction (mime, size, dimensions) and optimization tasks here or via signals
        super().save_model(request, obj, form, change)


@admin.register(ImageOptimizationProfile)
class ImageOptimizationProfileAdmin(admin.ModelAdmin):
    """Admin configuration for Image Optimization Profiles."""
    list_display = ('name', 'width', 'height', 'format', 'quality', 'is_active')
    list_filter = ('is_active', 'format')
    search_fields = ('name',)
