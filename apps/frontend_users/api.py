from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from .models import FrontEndUser, STATUS_INACTIVE # Import status constant if needed for logic

class FrontEndUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the FrontEndUser model (primarily for read operations or admin views).
    Handles public-facing user data.
    """
    class Meta:
        model = FrontEndUser
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'display_name', 'status', 'is_active', # Added status
            'date_joined', 'last_login',
            # Add other public profile fields here (e.g., 'avatar', 'bio')
        ]
        # Status and is_active might be read-only depending on workflow (e.g., email verification)
        read_only_fields = ['id', 'status', 'is_active', 'date_joined', 'last_login', 'email', 'username']
        extra_kwargs = {
            'display_name': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

# --- Specific Serializers for Auth/Profile Actions ---

class FrontEndUserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer specifically for user registration."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, required=True, label=_("Confirm password"), style={'input_type': 'password'}
    )

    class Meta:
        model = FrontEndUser
        fields = ('email', 'username', 'display_name', 'first_name', 'last_name', 'password', 'password2')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'display_name': {'required': False}, # Defaults to username in model save
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        # Add any other custom validation (e.g., check if email/username already exists, though handled by unique=True)
        return attrs

    def create(self, validated_data):
        # Remove password2 before creating user
        validated_data.pop('password2')
        # Use the manager's create_user method
        # Note: create_user expects specific args, pass others via extra_fields if manager was not updated
        # Assuming manager handles all fields passed in validated_data correctly now
        user = FrontEndUser.objects.create_user(**validated_data)
        # TODO: Implement email verification logic here if needed
        # user.status = STATUS_INACTIVE
        # user.save()
        # Send verification email task...
        return user


class FrontEndUserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing/updating the current user's profile."""
    class Meta:
        model = FrontEndUser
        # Exclude sensitive fields like password, status, is_active
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'display_name', 'date_joined')
        read_only_fields = ('id', 'email', 'username', 'date_joined') # Prevent changing email/username via profile update


# Add serializers for Password Reset if needed (e.g., PasswordResetSerializer, PasswordResetConfirmSerializer)
# These typically handle token generation/validation and password setting.