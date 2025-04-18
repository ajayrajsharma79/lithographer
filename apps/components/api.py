from rest_framework import serializers
from .models import ComponentDefinition, ComponentFieldDefinition

class ComponentFieldDefinitionSerializer(serializers.ModelSerializer):
    """Read-only serializer for ComponentFieldDefinition."""
    class Meta:
        model = ComponentFieldDefinition
        fields = ['id', 'name', 'api_id', 'field_type', 'order', 'config']
        read_only_fields = fields


class ComponentDefinitionSerializer(serializers.ModelSerializer):
    """Read-only serializer for ComponentDefinition."""
    field_definitions = ComponentFieldDefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = ComponentDefinition
        fields = ['id', 'name', 'api_id', 'description', 'icon', 'field_definitions']
        read_only_fields = fields

# Note: PageComponent data is typically retrieved/managed via the
# ContentInstance API endpoint it belongs to, not directly via its own endpoint.
# The ContentInstanceSerializer needs modification to include this layout data.