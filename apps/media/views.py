from rest_framework import viewsets, permissions, parsers, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Folder, MediaTag, MediaAsset, ImageOptimizationProfile
from .api import (
    FolderSerializer, MediaTagSerializer, MediaAssetSerializer,
    ImageOptimizationProfileSerializer
)

# Basic Permissions (Refine as needed)
class IsAdminOrUploaderOrReadOnly(permissions.BasePermission):
    """
    Allow read-only for anyone authenticated.
    Allow write/delete only for admins or the original uploader.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Write permissions check
        return request.user and (request.user.is_staff or obj.uploader == request.user)

class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class FolderViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Folders."""
    queryset = Folder.objects.select_related('parent').all().order_by('name')
    serializer_class = FolderSerializer
    permission_classes = [IsAdminUser] # Only admins manage folders for now


class MediaTagViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Media Tags."""
    queryset = MediaTag.objects.all().order_by('name')
    serializer_class = MediaTagSerializer
    permission_classes = [IsAdminUser] # Only admins manage tags for now
    lookup_field = 'slug'


class MediaAssetViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Media Assets."""
    queryset = MediaAsset.objects.select_related('folder', 'uploader').prefetch_related('tags').all().order_by('-upload_timestamp')
    serializer_class = MediaAssetSerializer
    # Use specific parser for file uploads
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    permission_classes = [permissions.IsAuthenticated, IsAdminOrUploaderOrReadOnly] # Must be logged in, check obj perms
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['folder', 'mime_type', 'tags', 'uploader']
    search_fields = ['title', 'filename', 'alt_text', 'caption', 'tags__name']
    ordering_fields = ['upload_timestamp', 'title', 'filename', 'size']

    # Override perform_destroy if specific cleanup is needed (e.g., delete file from storage)
    # def perform_destroy(self, instance):
    #     # Delete file from storage first
    #     if instance.file:
    #         instance.file.delete(save=False) # False avoids saving model again
    #     super().perform_destroy(instance)


class ImageOptimizationProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for managing Image Optimization Profiles."""
    queryset = ImageOptimizationProfile.objects.all().order_by('name')
    serializer_class = ImageOptimizationProfileSerializer
    permission_classes = [IsAdminUser] # Only admins manage profiles
