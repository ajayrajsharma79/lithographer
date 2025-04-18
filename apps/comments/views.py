from rest_framework import generics, permissions, mixins, viewsets
from django.shortcuts import get_object_or_404

from .models import Comment, STATUS_APPROVED
from .api import CommentSerializer
from apps.content.models import ContentInstance
from apps.frontend_users.models import FrontEndUser # For permission check

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `user`.
        # Ensure user is authenticated and is a FrontEndUser
        return (
            obj.user == request.user and
            isinstance(request.user, FrontEndUser)
        )

class CommentCreateView(generics.CreateAPIView):
    """
    API endpoint for creating comments on a specific ContentInstance.
    Accessed via /api/content/{instance_pk}/comments/
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated] # Must be logged in

    def perform_create(self, serializer):
        # Check if the user is a FrontEndUser before allowing comment creation
        if not isinstance(self.request.user, FrontEndUser):
             from rest_framework.exceptions import PermissionDenied
             raise PermissionDenied("Only registered front-end users can post comments.")

        instance_pk = self.kwargs.get('instance_pk')
        content_instance = get_object_or_404(ContentInstance, pk=instance_pk)
        # Status is set to PENDING by default in the serializer create method
        serializer.save(user=self.request.user, content_instance=content_instance)
        # TODO: Trigger 'comment_submitted' webhook event here or via signal


class CommentListView(generics.ListAPIView):
     """
     API endpoint for listing APPROVED comments for a specific ContentInstance.
     Accessed via /api/content/{instance_pk}/comments/ (GET)
     Note: This might conflict with CreateAPIView if not handled by router or explicit GET/POST handlers.
     Consider using a ViewSet or separate URLs if needed.
     For now, assumes separate handling or router usage.
     """
     serializer_class = CommentSerializer # Use the main serializer for listing? Or ReadCommentSerializer?
     permission_classes = [permissions.AllowAny] # Anyone can read approved comments

     def get_queryset(self):
         instance_pk = self.kwargs.get('instance_pk')
         content_instance = get_object_or_404(ContentInstance, pk=instance_pk)
         # Only return top-level approved comments; replies handled by serializer if using ReadCommentSerializer
         return Comment.objects.filter(
             content_instance=content_instance,
             status=STATUS_APPROVED,
             parent__isnull=True # Only top-level comments
         ).select_related('user').prefetch_related('replies') # Optimize


# Optional: ViewSet for managing own comments (e.g., edit/delete within a time limit)
# class UserCommentViewSet(mixins.UpdateModelMixin,
#                          mixins.DestroyModelMixin,
#                          viewsets.GenericViewSet):
#     serializer_class = CommentSerializer
#     permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
#
#     def get_queryset(self):
#         # Users can only manage their own comments
#         if isinstance(self.request.user, FrontEndUser):
#             return Comment.objects.filter(user=self.request.user)
#         return Comment.objects.none()
#
#     # Add logic to prevent editing/deleting after a certain time?
