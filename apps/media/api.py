from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Folder, MediaTag, MediaAsset, ImageOptimizationProfile
from apps.users.api import CMSUserSerializer # For uploader info

class FolderSerializer(serializers.ModelSerializer):
    """Serializer for Folders."""
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all(), source='parent', allow_null=True, required=False
    )
    # Add counts or nested data if needed
    # asset_count = serializers.IntegerField(read_only=True)
    # subfolder_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class MediaTagSerializer(serializers.ModelSerializer):
    """Serializer for Media Tags."""
    class Meta:
        model = MediaTag
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at'] # Slug generated automatically


class MediaAssetSerializer(serializers.ModelSerializer):
    """Serializer for Media Assets."""
    uploader_detail = CMSUserSerializer(source='uploader', read_only=True)
    folder_id = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all(), source='folder', allow_null=True, required=False
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=MediaTag.objects.all(), source='tags', many=True, required=False
    )
    # Expose file URL directly
    file_url = serializers.URLField(read_only=True)
    # Expose dimensions as a sub-object
    dimensions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MediaAsset
        fields = [
            'id',
            'translated_title', 'translated_alt_text', 'translated_caption', # Replaced fields
            'file', 'file_url', 'filename', 'mime_type', 'size',
            'width', 'height', 'dimensions',
            'folder_id', 'tags', 'tag_ids',
            'custom_metadata', 'uploader', 'uploader_detail', 'upload_timestamp',
            'optimized_versions'
        ]
        read_only_fields = [
            'id', 'file_url', 'filename', 'mime_type', 'size', 'width', 'height',
            'dimensions', 'uploader_detail', 'upload_timestamp', 'optimized_versions'
        ]
        extra_kwargs = {
            'file': {'write_only': True, 'required': True}, # File required on upload
            'uploader': {'write_only': True, 'required': False}, # Set automatically
            'tags': {'write_only': True}, # Use tag_ids for input
            # JSON fields are directly writable/readable
        }

    def get_dimensions(self, obj):
        if obj.width and obj.height:
            return {'width': obj.width, 'height': obj.height}
        return None

    def create(self, validated_data):
        # Set uploader automatically
        validated_data['uploader'] = self.context['request'].user
        # Extract tags data if provided via tag_ids
        tags_data = validated_data.pop('tags', None)

        instance = super().create(validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        # TODO: Trigger async task for metadata extraction and optimization
        # from .tasks import process_media_asset
        # process_media_asset.delay(instance.id)

        return instance

    def update(self, instance, validated_data):
         # File cannot be changed via update, only metadata
        validated_data.pop('file', None)
        # Uploader cannot be changed
        validated_data.pop('uploader', None)
        # Extract tags data if provided via tag_ids
        tags_data = validated_data.pop('tags', None)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        # TODO: Optionally trigger re-optimization if relevant metadata changed?

        return instance


class ImageOptimizationProfileSerializer(serializers.ModelSerializer):
    """Serializer for Image Optimization Profiles."""
    class Meta:
        model = ImageOptimizationProfile
        fields = ['id', 'name', 'width', 'height', 'format', 'quality', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']