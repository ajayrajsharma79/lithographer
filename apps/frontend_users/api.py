from rest_framework import serializers
from .models import FrontEndUser

class FrontEndUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the FrontEndUser model.
    Handles public-facing user data.
    """
    class Meta:
        model = FrontEndUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', # Added fields
            'display_name', 'is_active',
            'date_joined', 'last_login',
            # Add other public profile fields here (e.g., 'avatar', 'bio')
            'password' # Include password for creation/update (write-only)
        ]
        read_only_fields = ['id', 'is_active', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}, 'required': False},
            'email': {'required': True},
            'username': {'required': True},
            'display_name': {'required': True},
            # first_name and last_name are optional (blank=True in model)
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def create(self, validated_data):
        # Use the custom manager's create_user method
        # Ensure password is provided for creation
        if 'password' not in validated_data:
            raise serializers.ValidationError({'password': _('Password is required for new users.')})
        # create_user expects specific args, pass others via extra_fields
        create_args = {
            'email': validated_data.get('email'),
            'username': validated_data.get('username'),
            'display_name': validated_data.get('display_name'),
            'password': validated_data.get('password'),
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            # Pass any other fields if added later
        }
        user = FrontEndUser.objects.create_user(**create_args)
        return user

    def update(self, instance, validated_data):
        # Handle password update specifically
        password = validated_data.pop('password', None)

        # Update other fields using the default ModelSerializer update
        instance = super().update(instance, validated_data)

        # Set password if provided
        if password:
            instance.set_password(password)
            instance.save(update_fields=['password'])

        return instance

    # Exclude sensitive fields like password_hash from default representation
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Ensure password field (even if write-only) doesn't leak
        ret.pop('password', None)
        return ret