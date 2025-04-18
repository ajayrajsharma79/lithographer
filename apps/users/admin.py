from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Permission, Role, APIKey

CMSUser = get_user_model()

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin configuration for the Permission model."""
    list_display = ('name', 'codename', 'description')
    search_fields = ('name', 'codename')
    ordering = ('codename',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin configuration for the Role model."""
    list_display = ('name', 'description', 'is_system_role')
    list_filter = ('is_system_role',)
    search_fields = ('name',)
    ordering = ('name',)
    filter_horizontal = ('permissions',) # Use a nice widget for ManyToMany

    # Prevent deletion of system roles
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            # You might want a custom action that checks is_system_role
            # or modify the queryset for the delete action if possible.
            # For simplicity, we rely on the model's protection or override delete_queryset.
            pass
        return actions

    def delete_queryset(self, request, queryset):
        # Explicitly prevent deleting system roles in bulk actions
        queryset.exclude(is_system_role=True).delete()

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting individual system roles
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)


# Define a new User admin
@admin.register(CMSUser)
class CMSUserAdmin(BaseUserAdmin):
    """Admin configuration for the CMSUser model."""
    # Use the custom form from UserAdmin but adapt fields
    # form = UserChangeForm
    # add_form = UserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_roles_display')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'roles')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('roles', 'groups', 'user_permissions') # Include default auth fields if needed

    # Define fieldsets for the change form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'roles'), # Add roles here
        }),
        # Remove default 'groups' and 'user_permissions' if roles handle all permissions
        # Or keep them if you use a mix of Django's built-in perms and custom roles
        # (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
        #                               'groups', 'user_permissions', 'roles')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    # Define fieldsets for the add form (creation)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'password2'), # Use password2 for confirmation
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'roles'),
        }),
    )

    # Use email as the unique identifier
    readonly_fields = ('last_login', 'date_joined')

    # Override the default UserAdmin settings that rely on 'username'
    # USERNAME_FIELD = 'email' # Already set in model
    # ordering = ('email',) # Already set

    def get_roles_display(self, obj):
        """Displays roles in the list view."""
        return ", ".join([role.name for role in obj.roles.all()])
    get_roles_display.short_description = _('Roles')

    # If using custom creation form, ensure it handles email/password correctly
    # add_form = YourCustomUserCreationForm


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin configuration for the APIKey model."""
    list_display = ('name', 'user_email', 'key_prefix', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('is_active', 'user')
    search_fields = ('name', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('key', 'created_at', 'last_used_at') # Key should not be displayed fully or editable
    raw_id_fields = ('user',) # Use a simpler widget for ForeignKey to User

    fieldsets = (
        (None, {'fields': ('name', 'user', 'is_active')}),
        (_('Key Info (Read-Only)'), {'fields': ('key_prefix', 'created_at', 'last_used_at')}),
        # Add expiration fieldset if implemented
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('User Email')
    user_email.admin_order_field = 'user__email'

    def key_prefix(self, obj):
        """Show only a prefix of the key for security."""
        return f"{obj.key[:8]}..." if obj.key else "N/A"
    key_prefix.short_description = _('Key Prefix')

    # Prevent adding keys via admin? Usually done via API or user profile.
    # def has_add_permission(self, request):
    #     return False

    # Prevent changing keys via admin
    def has_change_permission(self, request, obj=None):
        # Allow changing name/is_active, but not the key itself (handled by readonly_fields)
        return super().has_change_permission(request, obj)

    # Prevent viewing the full key easily
    def get_readonly_fields(self, request, obj=None):
        # Always make key readonly, add others as needed
        return self.readonly_fields + ('key',)
