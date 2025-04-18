from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid

class FrontEndUserManager(BaseUserManager):
    """
    Custom manager for the FrontEndUser model.
    """
    def create_user(self, email, username, display_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        if not display_name:
            raise ValueError(_('The Display Name field must be set'))

        email = self.normalize_email(email)
        # Ensure is_staff and is_superuser are always false for frontend users
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        if extra_fields.get('is_staff') is True or extra_fields.get('is_superuser') is True:
             raise ValueError(_('FrontEndUser cannot be staff or superuser.'))

        user = self.model(email=email, username=username, display_name=display_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, display_name, password=None, **extra_fields):
        # Front-end users should never be superusers in the Django admin sense
        raise NotImplementedError(_("Cannot create a superuser for FrontEndUser model."))


# Status choices for FrontEndUser
STATUS_ACTIVE = 'active'
STATUS_INACTIVE = 'inactive' # e.g., email not verified
STATUS_BANNED = 'banned'
FRONTEND_USER_STATUS_CHOICES = [
    (STATUS_ACTIVE, _('Active')),
    (STATUS_INACTIVE, _('Inactive')),
    (STATUS_BANNED, _('Banned')),
]

class FrontEndUser(AbstractBaseUser, PermissionsMixin):
    """
    Represents a user of the public-facing website (e.g., commenters, members).
    Distinct from CMSUser (administrators, editors).
    Uses email for login but also requires a display name.
    Does not use Django's built-in groups or permissions directly,
    but includes PermissionsMixin for potential future custom permission needs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_("Used for login and notifications.")
    )
    username = models.CharField(
        _("Username"),
        max_length=150,
        unique=True,
        # null=True, # Removed after applying migrations
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        # Add validators if needed, e.g., ASCIIUsernameValidator
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    display_name = models.CharField(
        _("Display Name"),
        max_length=150,
        # unique=True, # Display name might not need to be unique if username is
        help_text=_("Publicly visible name (e.g., for comments). Defaults to username if blank.")
    )
    # Add other profile fields as needed: avatar, bio, website_url, etc.
    # avatar = models.ImageField(upload_to='frontend_avatars/', null=True, blank=True)
    # bio = models.TextField(blank=True)

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    # Frontend users are never staff/admin users in the Django sense
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into the Django admin site (always False for FrontEndUser).'),
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=FRONTEND_USER_STATUS_CHOICES,
        default=STATUS_ACTIVE, # Or STATUS_INACTIVE if email verification is required
        db_index=True,
        help_text=_("The current status of the front-end user account.")
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True) # Added last_login

    objects = FrontEndUserManager()

    # Add related_name to avoid clashes with other user models
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="frontenduser_set", # Unique related name
        related_query_name="frontenduser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="frontenduser_set", # Unique related name
        related_query_name="frontenduser",
    )

    USERNAME_FIELD = 'email'
    # Username and display name are required at creation time via the manager
    REQUIRED_FIELDS = ['username', 'display_name']

    class Meta:
        verbose_name = _("Front-End User")
        verbose_name_plural = _("Front-End Users")
        ordering = ['display_name']

    def __str__(self):
        return f"{self.display_name} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def save(self, *args, **kwargs):
        # Default display_name to username if blank
        if not self.display_name:
            self.display_name = self.username
        super().save(*args, **kwargs)

    # Since PermissionsMixin is included, has_perm and has_module_perms exist.
    # By default, without assigned permissions or superuser status, they will return False.
    # You might override these later if you implement custom frontend permissions.
    # For now, they correctly reflect that frontend users have no Django admin/model perms.
