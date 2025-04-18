from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from .models import (
    ContentType, FieldDefinition, Taxonomy, Term,
    ContentInstance, ContentFieldInstance, ContentVersion
)
from .api import (
    ContentTypeSerializer, TaxonomySerializer, TermSerializer,
    ContentInstanceSerializer, ContentVersionSerializer
)

# --- Basic Permissions ---
# Define more granular permissions later if needed
class IsAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only for anyone, write for admins."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsEditorUser(permissions.BasePermission):
     """Allows access only to users who are staff (includes admins)."""
     # This might need refinement based on specific Editor role/permissions
     def has_permission(self, request, view):
         return request.user and request.user.is_staff

# --- ViewSets ---

class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Content Types and their field definitions.
    Creation/modification is typically handled via the Admin UI.
    """
    queryset = ContentType.objects.prefetch_related('field_definitions').all().order_by('name')
    serializer_class = ContentTypeSerializer
    permission_classes = [permissions.IsAuthenticated] # Must be logged in to see types
    lookup_field = 'api_id'


class TaxonomyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Taxonomies.
    """
    queryset = Taxonomy.objects.prefetch_related('content_types').all().order_by('name')
    serializer_class = TaxonomySerializer
    permission_classes = [IsAdminUser] # Only Admins manage taxonomies
    lookup_field = 'api_id'


class TermViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Terms within a specific Taxonomy.
    Nested under /api/v1/taxonomies/{taxonomy_api_id}/terms/
    """
    serializer_class = TermSerializer
    permission_classes = [IsEditorUser] # Editors/Admins can manage terms

    def get_queryset(self):
        """Filter terms based on the taxonomy API ID from the URL."""
        taxonomy_api_id = self.kwargs.get('taxonomy_api_id')
        taxonomy = get_object_or_404(Taxonomy, api_id=taxonomy_api_id)
        # TODO: Add ordering based on hierarchy if needed (e.g., using django-mptt)
        return Term.objects.filter(taxonomy=taxonomy).select_related('parent').order_by('translated_names') # Basic ordering

    def perform_create(self, serializer):
        """Associate the term with the taxonomy from the URL."""
        taxonomy_api_id = self.kwargs.get('taxonomy_api_id')
        taxonomy = get_object_or_404(Taxonomy, api_id=taxonomy_api_id)
        serializer.save(taxonomy=taxonomy)

    def get_serializer_context(self):
        """Add taxonomy to context for validation if needed."""
        context = super().get_serializer_context()
        if 'taxonomy_api_id' in self.kwargs:
            context['taxonomy'] = get_object_or_404(Taxonomy, api_id=self.kwargs['taxonomy_api_id'])
        return context


class ContentInstanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Content Instances.
    Handles CRUD operations and dynamic field data.
    """
    serializer_class = ContentInstanceSerializer
    permission_classes = [IsEditorUser] # Editors/Admins manage content

    def get_queryset(self):
        """
        Return Content Instances, potentially filtered by ContentType.
        Prefetch related data for efficiency.
        """
        queryset = ContentInstance.objects.select_related(
            'content_type', 'author'
        ).prefetch_related(
            # Prefetch field instances efficiently
            Prefetch('field_instances', queryset=ContentFieldInstance.objects.select_related('field_definition', 'language')),
            Prefetch('terms', queryset=Term.objects.select_related('taxonomy')) # Prefetch terms
        ).all().order_by('-updated_at')

        # Optional filtering by content type api_id if provided in query params
        content_type_api_id = self.request.query_params.get('content_type', None)
        if content_type_api_id:
            queryset = queryset.filter(content_type__api_id=content_type_api_id)

        return queryset

    def perform_create(self, serializer):
        """Set author during creation."""
        # ContentType is set via request data, validated by serializer
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Author is not changed on update by default
        serializer.save()

    # Add action for viewing versions
    @action(detail=True, methods=['get'], url_path='versions', permission_classes=[IsEditorUser])
    def list_versions(self, request, pk=None):
        """Retrieve the version history for a Content Instance."""
        instance = self.get_object()
        versions = instance.versions.select_related('created_by').order_by('-created_at')
        # Paginate results if needed
        page = self.paginate_queryset(versions)
        if page is not None:
            serializer = ContentVersionSerializer(page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

        serializer = ContentVersionSerializer(versions, many=True, context=self.get_serializer_context())
        return Response(serializer.data)

    # Add action for retrieving a specific version
    @action(detail=True, methods=['get'], url_path='versions/(?P<version_pk>[^/.]+)', permission_classes=[IsEditorUser])
    def retrieve_version(self, request, pk=None, version_pk=None):
        """Retrieve a specific version snapshot."""
        instance = self.get_object() # Ensure instance exists and user has permission
        version = get_object_or_404(instance.versions.select_related('created_by'), pk=version_pk)
        serializer = ContentVersionSerializer(version, context=self.get_serializer_context())
        return Response(serializer.data)

    # Action to revert to a specific version? (More complex)
    # @action(detail=True, methods=['post'], url_path='versions/(?P<version_pk>[^/.]+)/revert')
    # def revert_to_version(self, request, pk=None, version_pk=None):
    #     instance = self.get_object()
    #     version = get_object_or_404(instance.versions, pk=version_pk)
    #     # Logic to apply version.data_snapshot back to instance fields
    #     # Needs careful implementation similar to serializer update logic
    #     # ...
    #     # Create a new version indicating the revert
    #     ContentVersion.create_version(instance, user=request.user, message=f"Reverted to version {version_pk}")
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)


class ContentVersionViewSet(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """
    Read-only API endpoint for viewing Content Versions globally.
    Filtering by content instance is recommended via query parameters
    or by using the nested actions on ContentInstanceViewSet.
    """
    queryset = ContentVersion.objects.select_related('content_instance', 'created_by').all().order_by('-created_at')
    serializer_class = ContentVersionSerializer
    permission_classes = [IsAdminUser] # Only Admins view all versions globally? Or Editors?

    # Add filtering by content_instance_id, user, date range etc.
    # filter_backends = [...]
    # filterset_fields = ['content_instance', 'created_by', 'status_snapshot']
