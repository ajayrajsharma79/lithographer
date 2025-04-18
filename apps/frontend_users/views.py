from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FrontEndUser
from .api import FrontEndUserSerializer

# Permissions for frontend users might be more complex (e.g., allow self-registration)
# For now, let's assume only admins can manage them via this specific API endpoint,
# but other endpoints (e.g., for registration) might have different permissions.
class FrontEndUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Front-End Users (public site users).
    Permissions might vary depending on the action (e.g., public registration vs admin management).
    """
    queryset = FrontEndUser.objects.all().order_by('display_name')
    serializer_class = FrontEndUserSerializer
    # Default permission: Only Admin users can list/create/delete/update via this endpoint
    permission_classes = [permissions.IsAdminUser]

    # Example: Override permissions for specific actions if needed
    # def get_permissions(self):
    #     if self.action == 'create': # Allow anyone to create (register)
    #         return [permissions.AllowAny()]
    #     elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
    #          # Allow users to manage their own account, or admins to manage any
    #         return [permissions.IsAuthenticated, IsOwnerOrAdmin()] # Custom permission needed
    #     return super().get_permissions()

    # Add filtering/search if needed
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['email', 'display_name']
    # ordering_fields = ['email', 'display_name', 'date_joined']

    # Note: A separate registration endpoint is usually recommended over exposing
    # the 'create' action directly in a ModelViewSet intended for admin use.
