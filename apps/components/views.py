from rest_framework import viewsets, permissions

from .models import ComponentDefinition
from .api import ComponentDefinitionSerializer

class ComponentDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing available Component Definitions.
    These are typically managed via the Admin UI.
    """
    queryset = ComponentDefinition.objects.prefetch_related('field_definitions').all().order_by('name')
    serializer_class = ComponentDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated] # Allow any authenticated user to see available components
    lookup_field = 'api_id'

# No viewset needed for PageComponent directly, as it's managed
# via the ContentInstance admin inline and its data included in the
# ContentInstance API response.
