from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import secrets
import uuid

# Removed the Permission model. Permissions will be string-based.

class Role(models.Model):
    """
    Represents a user role within the CMS, grouping multiple permissions.
    """
    # Predefined role constants
    ADMINISTRATOR = 'administrator'
    EDITOR = 'editor'
    MODERATOR = 'moderator'
    ROLE_CHOICES = [
        (ADMINISTRATOR, _('Administrator')),
        (EDITOR, _('Editor')),
        (MODERATOR, _('Moderator')),
        # Add other roles as needed
    ]

    name = models.CharField(
        _("Role Name"),
        max_length=100,
        unique=True,
        help_text=_("Unique name for the role (e.g., 'Administrator', 'Editor').")
    )
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Optional description of the role's purpose.")
    )
    # Store permissions as a list of strings in a JSON field
    permissions = models.JSONField(
        _("Permissions"),
        default=list,
        blank=True,
        help_text=_("List of permission strings granted to this role (e.g., ['content.add_contentinstance', 'content.publish_blogpost']). Use '*' for all permissions.")
    )
    is_system_role = models.BooleanField(
        _("Is System Role"),
        default=False,
        help_text=_("System roles (like Administrator) cannot be deleted.")
    )

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ['name']

    def __str__(self):
        return self.name

    # Consider adding methods to easily check for predefined roles if needed
    # e.g., @property def is_administrator(self): return self.name == self.ADMINISTRATOR


class CMSUserManager(BaseUserManager):
    """
    Custom manager for the CMSUser model.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        # Ensure the Administrator role exists and assign it
        admin_role, created = Role.objects.get_or_create(
            name=Role.ADMINISTRATOR,
            defaults={'description': 'Full system access', 'is_system_role': True}
        )
        # You might want to assign all permissions to the admin role here if needed

        user = self.create_user(email, password, **extra_fields)
        user.roles.add(admin_role) # Assign the admin role
        return user


class CMSUser(AbstractUser, PermissionsMixin):
    """
    Custom User model for CMS administrators, editors, etc.
    Uses email as the unique identifier instead of username.
    """
    # Remove username field from AbstractUser, use email instead
    username = None
    email = models.EmailField(_('email address'), unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name="users",
        verbose_name=_("Roles"),
        help_text=_("Roles assigned to this user.")
    )
    # Add any other CMS user-specific fields here (e.g., profile picture, bio)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] # Add fields required for createsuperuser

    # Add related_name to avoid clashes with other user models
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="cmsuser_set", # Unique related name
        related_query_name="cmsuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="cmsuser_set", # Unique related name
        related_query_name="cmsuser",
    )

    objects = CMSUserManager()

    class Meta:
        verbose_name = _("CMS User")
        verbose_name_plural = _("CMS Users")
        ordering = ['email']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    # Granular permission checking - override has_perm
    def has_perm(self, perm, obj=None):
        """
        Checks if the user has a specific permission codename.
        Overrides the default Django permission check.
        Checks permissions directly assigned via roles.
        Superusers implicitly have all permissions.
        """
        # Active superusers have all permissions
        if self.is_active and self.is_superuser:
            return True

        # Check permissions granted through assigned roles
        # Use prefetch_related('roles') in views for efficiency
        for role in self.roles.all():
            if "*" in role.permissions: # Check for wildcard permission
                return True
            if perm in role.permissions:
                return True
        return False # Permission not found in any role

    # has_perms (plural) is usually handled by checking has_perm for each perm in the list
    # has_module_perms is often used by the Django admin
    def has_module_perms(self, app_label):
        """
        Does the user have permissions to view the app `app_label`?
        Simplest possible answer: Yes, if the user is active and staff.
        A more granular check could be implemented based on roles/permissions.
        """
        return self.is_active and self.is_staff


def generate_api_key():
    """Generates a secure random API key."""
    return secrets.token_urlsafe(32) # Generates a 32-byte key

class APIKey(models.Model):
    """
    Represents an API key for external system access.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(
        _("API Key"),
        max_length=100, # Adjust length based on generation method
        unique=True,
        default=generate_api_key,
        editable=False, # Key should not be editable after creation
        help_text=_("The unique API key string.")
    )
    user = models.ForeignKey(
        CMSUser,
        on_delete=models.CASCADE, # Or SET_NULL if key should persist if user deleted
        related_name="api_keys",
        verbose_name=_("Associated User"),
        help_text=_("The CMS user associated with this key.")
    )
    name = models.CharField(
        _("Key Name"),
        max_length=100,
        help_text=_("A descriptive name for the API key (e.g., 'External Blog Integration').")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    last_used_at = models.DateTimeField(_("Last Used At"), null=True, blank=True)
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Whether the API key is currently active.")
    )
    # Optional: Add expiration date
    # expires_at = models.DateTimeField(_("Expires At"), null=True, blank=True)

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    def record_usage(self):
        """Updates the last used timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])

    # Consider adding permission scoping to API keys in the future
