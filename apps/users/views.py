from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Role, APIKey # Removed Permission import
from .api import RoleSerializer, CMSUserSerializer, APIKeySerializer # Removed PermissionSerializer

CMSUser = get_user_model()

# Removed PermissionViewSet as Permission model was removed

class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows roles to be viewed or edited.
    System roles cannot be deleted.
    """
    queryset = Role.objects.all().prefetch_related('permissions').order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can manage roles

    def perform_destroy(self, instance):
        # Prevent deletion of system roles
        if instance.is_system_role:
            raise permissions.PermissionDenied("System roles cannot be deleted.")
        super().perform_destroy(instance)


class CMSUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows CMS users to be viewed or edited.
    """
    queryset = CMSUser.objects.all().prefetch_related('roles').order_by('email')
    serializer_class = CMSUserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins manage CMS users via API

    # Add filtering/search capabilities if needed
    # filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    # search_fields = ['email', 'first_name', 'last_name']
    # ordering_fields = ['email', 'date_joined', 'last_login']

    # Optional: Action for current user to view/update their own profile
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            # Prevent users from making themselves staff/superuser via 'me' endpoint
            # Or changing roles unless specifically allowed
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(user, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            # Explicitly check for disallowed field changes
            disallowed_fields = ['is_staff', 'is_superuser', 'roles']
            for field in disallowed_fields:
                if field in serializer.validated_data:
                     # Allow if the value isn't actually changing (e.g. PATCHing other fields)
                    if getattr(user, field) != serializer.validated_data[field]:
                         # Special case: allow roles if it's just setting to existing roles
                        if field == 'roles':
                            current_roles = set(user.roles.all())
                            new_roles = set(serializer.validated_data[field])
                            if current_roles == new_roles:
                                continue # No actual change in roles
                        # Otherwise, deny
                        raise permissions.PermissionDenied(f"You cannot modify the '{field}' field for your own account via this endpoint.")


            serializer.save()
            return Response(serializer.data)


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows API keys to be viewed or managed.
    Users can manage their own keys. Admins can manage all keys.
    """
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated] # Must be logged in

    def get_queryset(self):
        """
        Filter keys based on the user. Admins see all, others see only their own.
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return APIKey.objects.all().select_related('user').order_by('-created_at')
        return APIKey.objects.filter(user=user).select_related('user').order_by('-created_at')

    def perform_create(self, serializer):
        """Associate the new key with the requesting user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure users can only update their own keys unless they are admin
        # The get_queryset already filters, but this adds an explicit check
        instance = serializer.instance
        if not self.request.user.is_staff and instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only update your own API keys.")
        serializer.save()

    def perform_destroy(self, instance):
         # Ensure users can only delete their own keys unless they are admin
        if not self.request.user.is_staff and instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own API keys.")
        super().perform_destroy(instance)
