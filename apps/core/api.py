from rest_framework import serializers
from .models import Language, SystemSetting

class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Language model.
    """
    class Meta:
        model = Language
        fields = ['code', 'name', 'is_active', 'is_default']
        read_only_fields = ['is_default'] # is_default is managed by model logic

class SystemSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for the SystemSetting singleton model.
    Provides default_language code for representation.
    """
    # Use SlugRelatedField to represent the related language by its code
    default_language_code = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Language.objects.filter(is_active=True),
        source='default_language', # Map this field to the default_language model field
        allow_null=True,
        required=False,
        help_text="Language code (e.g., 'en') of the active default language."
    )

    class Meta:
        model = SystemSetting
        fields = ['site_name', 'default_language_code', 'timezone']
        # No read_only_fields needed here as it's a singleton managed via its view

    def update(self, instance, validated_data):
        # Handle setting default_language via code
        # The source='default_language' on default_language_code handles the lookup
        # during validation if the code exists in the queryset.
        # The instance is automatically updated by super().update()
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Ensure default_language_code is included in the output."""
        representation = super().to_representation(instance)
        representation['default_language_code'] = instance.default_language.code if instance.default_language else None
        return representation