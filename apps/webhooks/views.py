from rest_framework import viewsets, permissions, mixins
from django.utils import timezone

from .models import WebhookEndpoint, WebhookEventLog
from .api import WebhookEndpointSerializer, WebhookEventLogSerializer

class WebhookEndpointViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows webhook endpoints to be viewed or managed.
    Users with appropriate permissions (e.g., admins or specific roles) can manage these.
    """
    serializer_class = WebhookEndpointSerializer
    permission_classes = [permissions.IsAdminUser] # Restrict to admins by default

    def get_queryset(self):
        """
        Return all webhook endpoints. Admins manage these globally.
        Could be adapted if non-admins need to manage specific endpoints.
        """
        return WebhookEndpoint.objects.all().select_related('created_by').order_by('-created_at')

    # perform_create is handled by the serializer default setting created_by


class WebhookEventLogViewSet(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """
    API endpoint that allows webhook event logs to be viewed.
    Logs are read-only via the API.
    """
    queryset = WebhookEventLog.objects.all().select_related('endpoint').order_by('-timestamp')
    serializer_class = WebhookEventLogSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can view logs by default

    # Add filtering capabilities (e.g., by endpoint, status, event_type, date range)
    # filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # filterset_fields = ['endpoint', 'status', 'event_type']
    # ordering_fields = ['timestamp', 'status', 'event_type']
    # ordering = ['-timestamp']

# Placeholder for the view/task that actually triggers webhooks
# This would likely involve:
# 1. Receiving an internal signal or call when an event occurs (e.g., content published).
# 2. Querying active WebhookEndpoints subscribed to that event.
# 3. For each endpoint, creating a Celery task to send the payload.
# 4. The Celery task would:
#    - Construct the payload.
#    - Generate the signature using endpoint.generate_signature().
#    - Make the HTTP POST request.
#    - Create a WebhookEventLog entry with the request details and response.
#    - Update the log entry status (success/failed) based on the response.
