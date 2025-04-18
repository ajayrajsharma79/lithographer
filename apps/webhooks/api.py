from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import WebhookEndpoint, WebhookEventLog
from apps.users.api import CMSUserSerializer # Reuse user serializer for created_by

CMSUser = get_user_model()

class WebhookEndpointSerializer(serializers.ModelSerializer):
    """Serializer for the WebhookEndpoint model."""
    # Show user detail on read, allow setting via PK on write
    created_by_detail = CMSUserSerializer(source='created_by', read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        # Provide the queryset of all possible users for validation
        queryset=CMSUser.objects.all(),
        write_only=True,
        required=False, # Allow setting automatically
        default=serializers.CurrentUserDefault() # Set to current user on create
    )

    class Meta:
        model = WebhookEndpoint
        fields = [
            'id', 'target_url', 'subscribed_events', 'is_active',
            'created_at', 'updated_at', 'created_by', 'created_by_detail',
            'secret' # Include secret for creation/update
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            # Make secret write-only for security - it shouldn't be exposed via API once set.
            # Consider a separate endpoint or mechanism if secret retrieval is needed.
            'secret': {'write_only': True, 'style': {'input_type': 'password'}, 'required': True},
            'created_by': {'write_only': True},
        }

    def create(self, validated_data):
        # Ensure created_by is set if not provided explicitly
        if 'created_by' not in validated_data and self.context['request'].user.is_authenticated:
             validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    # Note: Updating the secret might require special handling depending on security policy.
    # The current setup allows overwriting it.

class WebhookEventLogSerializer(serializers.ModelSerializer):
    """Serializer for the WebhookEventLog model (typically read-only via API)."""
    # Represent endpoint by its URL
    endpoint_url = serializers.URLField(source='endpoint.target_url', read_only=True)

    class Meta:
        model = WebhookEventLog
        fields = [
            'id', 'endpoint_url', 'event_type', 'payload',
            'request_headers', 'response_status_code', 'response_headers', 'response_body',
            'status', 'timestamp', 'is_successful'
        ]
        read_only_fields = fields # Logs are generally not created/modified via API


# Note: ViewSets will be needed to expose these serializers via URLs.