from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model # If needed for other actions

from .models import FrontEndUser
from .api import (
    FrontEndUserSerializer,
    FrontEndUserRegistrationSerializer,
    FrontEndUserProfileSerializer,
)

# --- API Views for Front-End User Actions ---

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for Front-End User registration.
    Allows any user (unauthenticated) to create an account.
    """
    queryset = FrontEndUser.objects.all()
    serializer_class = FrontEndUserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Optionally return user data (excluding password) or just success message
        # Consider returning tokens immediately upon registration if email verification is not used
        # For now, return basic user info from the default serializer
        output_serializer = FrontEndUserSerializer(user, context=self.get_serializer_context())
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating the current authenticated user's profile.
    """
    queryset = FrontEndUser.objects.all()
    serializer_class = FrontEndUserProfileSerializer
    permission_classes = [permissions.IsAuthenticated] # Must be logged in

    def get_object(self):
        # Return the profile of the currently authenticated user
        # Ensure request.user is an instance of FrontEndUser
        # This might require custom authentication backend or checks if mixing user types
        if isinstance(self.request.user, FrontEndUser):
            return self.request.user
        else:
            # Handle cases where the authenticated user is not a FrontEndUser (e.g., CMSUser)
            # Option 1: Raise an error
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only Front-End Users can access this profile endpoint.")
            # Option 2: Return None or handle differently based on requirements
            # return None

    # PUT is disabled by default in RetrieveUpdateAPIView unless implemented
    # PATCH is enabled for partial updates


# --- Admin Management ViewSet (Optional - if needed beyond Django Admin) ---

class FrontEndUserAdminViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Admins to manage Front-End Users.
    Provides full CRUD, but actions like registration/password reset
    should use dedicated endpoints above.
    """
    queryset = FrontEndUser.objects.all().order_by('username')
    serializer_class = FrontEndUserSerializer # Use the basic serializer for admin view
    permission_classes = [permissions.IsAdminUser] # Only Admins

    # Add actions for ban/activate/deactivate if needed
    # @action(detail=True, methods=['post'])
    # def ban(self, request, pk=None): ...
    # @action(detail=True, methods=['post'])
    # def activate(self, request, pk=None): ...


# --- Placeholder Views for Password Reset ---
# These would typically involve generating tokens, sending emails (via Celery),
# and validating tokens upon confirmation. Libraries like django-rest-passwordreset
# can simplify this significantly.

# @api_view(['POST'])
# @permission_classes([permissions.AllowAny])
# def password_reset_request(request):
#     # Validate email exists
#     # Generate reset token
#     # Send email via Celery task
#     return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes([permissions.AllowAny])
# def password_reset_confirm(request):
#     # Validate token, uid, new password
#     # Set new password
#     return Response({"message": "Password has been reset."}, status=status.HTTP_200_OK)
