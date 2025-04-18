from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Use parts of it if helpful
from django.utils.translation import gettext_lazy as _

from .models import FrontEndUser

# Since FrontEndUser uses AbstractBaseUser, we need a more custom admin class
@admin.register(FrontEndUser)
class FrontEndUserAdmin(admin.ModelAdmin):
    """Admin configuration for the FrontEndUser model."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'display_name', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_active', 'date_joined', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'display_name')
    ordering = ('username',) # Order by username
    readonly_fields = ('date_joined', 'last_login', 'password') # Password hash shouldn't be edited directly

    # Define fieldsets for the change form
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}), # Password shown readonly
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'display_name')}),
        # Add other profile fields here if they exist (e.g., 'avatar', 'bio')
        (_('Status'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        # Note: PermissionsMixin fields ('is_superuser', 'groups', 'user_permissions')
        # are inherited but likely not used/relevant for FrontEndUser in the admin.
        # We exclude them from fieldsets. 'is_staff' is forced False by the model manager.
    )

    # Define fields for the add form (creation)
    # Note: Admin creation might bypass some logic in the manager (like password requirement)
    # It's often better to disable admin creation or use a custom form.
    # Add form is disabled by has_add_permission, so add_fieldsets is not strictly needed
    # but kept here for reference if add permission is enabled later.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Need a custom form to handle password creation properly if enabling add
            'fields': ('username', 'email', 'first_name', 'last_name', 'display_name'),
        }),
         (_('Status'), {'fields': ('is_active',)}),
    )
    # Add a placeholder field for the add form if not using a custom form
    # readonly_fields = ('date_joined', 'last_login', 'password_prompt') # Make prompt readonly too

    # If allowing creation via admin, consider how password is set.
    # A custom form is the best way. For simplicity here, we might disable add:
    def has_add_permission(self, request):
        # Disable adding frontend users directly via admin by default
        # Recommend using API or frontend registration flow
        return False

    # Prevent direct password editing
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Optionally remove password from change view entirely if needed
        # Or ensure it's always readonly
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        # Ensure password field is always readonly in the change view
        ro_fields = list(super().get_readonly_fields(request, obj))
        if 'password' not in ro_fields:
            ro_fields.append('password')
        # Add password_prompt if it exists for the add view context
        if obj is None and 'password_prompt' not in ro_fields:
             ro_fields.append('password_prompt')
        return tuple(ro_fields)

    # Add a non-model field for the add form password prompt
    # password_prompt = models.CharField(max_length=1, default='', editable=False) # Hacky way
