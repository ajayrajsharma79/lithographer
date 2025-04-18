from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _

from .models import Language, SystemSetting
from .api import LanguageSerializer, SystemSettingSerializer

class LanguageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows languages to be viewed or edited.
    """
    queryset = Language.objects.all().order_by('name')
    serializer_class = LanguageSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can manage languages
    lookup_field = 'code' # Use language code as the lookup field

    # Optional: Action to set a language as default
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def set_default(self, request, code=None):
        language = self.get_object()
        try:
            # Ensure the language is active before setting as default
            if not language.is_active:
                return Response(
                    {'error': _('Cannot set an inactive language as default.')},
                    status=status.HTTP_400_BAD_REQUEST
                )
            language.is_default = True
            language.save()
            # Update related SystemSetting if it exists
            system_settings = SystemSetting.load()
            if system_settings.default_language != language:
                system_settings.default_language = language
                system_settings.save(update_fields=['default_language'])

            return Response({'status': _('Language set as default')})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemSettingViewSet(viewsets.ViewSet):
    """
    API endpoint for viewing and editing the singleton System Settings.
    Uses ViewSet instead of ModelViewSet because there's only one object.
    """
    serializer_class = SystemSettingSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can manage settings

    def get_object(self):
        # Always return the singleton instance
        return SystemSetting.load()

    def list(self, request):
        """Get the current system settings."""
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def update(self, request, pk=None): # pk is ignored for singleton
        """Update the system settings."""
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=False) # Use partial=False for PUT
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, pk=None): # pk is ignored for singleton
        """Partially update the system settings."""
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True) # Use partial=True for PATCH
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # No create or destroy methods needed for a singleton
