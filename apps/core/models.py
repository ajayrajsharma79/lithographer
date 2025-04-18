from django.db import models
from django.utils.translation import gettext_lazy as _

class Language(models.Model):
    """
    Represents a language supported by the CMS.
    """
    code = models.CharField(
        _("Language Code"),
        max_length=10,
        unique=True,
        primary_key=True,
        help_text=_("Standard language code (e.g., 'en', 'en-us', 'fr')")
    )
    name = models.CharField(
        _("Language Name"),
        max_length=100,
        help_text=_("Full name of the language (e.g., 'English', 'French')")
    )
    is_active = models.BooleanField(
        _("Is Active"),
        default=True,
        help_text=_("Is this language currently available for use?")
    )
    is_default = models.BooleanField(
        _("Is Default"),
        default=False,
        help_text=_("Is this the default language for the site?")
    )

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # Ensure only one language can be default
        if self.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
        # Ensure at least one language is default if none are after save
        if not Language.objects.filter(is_default=True).exists():
            first_active = Language.objects.filter(is_active=True).first()
            if first_active:
                first_active.is_default = True
                first_active.save(update_fields=['is_default'])


class SystemSetting(models.Model):
    """
    Stores global system settings for the CMS.
    Uses a singleton pattern (only one instance should exist).
    """
    site_name = models.CharField(
        _("Site Name"),
        max_length=255,
        default="Lithographer CMS",
        help_text=_("The public name of the website.")
    )
    default_language = models.OneToOneField(
        Language,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+', # No reverse relation needed
        verbose_name=_("Default Language"),
        help_text=_("The default language for the site content and interface.")
    )
    timezone = models.CharField(
        _("Timezone"),
        max_length=100,
        default="UTC",
        help_text=_("Default timezone for the application (e.g., 'UTC', 'America/New_York').")
        # Consider using timezone_field package for validation if needed
    )
    # Store API keys/configs for external integrations
    external_integrations = models.JSONField(
        _("External Integrations Config"),
        default=dict,
        blank=True,
        help_text=_("Store API keys and settings for external services (e.g., {'google_analytics_id': 'UA-XXXXX-Y'}). Use with caution.")
    )
    # Global content settings
    default_content_status = models.CharField(
        _("Default Content Status"),
        max_length=20,
        # Use choices from content app - requires careful import or duplication
        # from apps.content.models import STATUS_CHOICES, STATUS_DRAFT
        choices=[('draft', 'Draft'), ('in_review', 'In Review'), ('published', 'Published')], # Simplified choices for now
        default='draft', # Default to draft
        help_text=_("The default status assigned to newly created content instances.")
    )
    # Add other global settings here as needed

    class Meta:
        verbose_name = _("System Setting")
        verbose_name_plural = _("System Settings")

    def __str__(self):
        return _("System Settings")

    def save(self, *args, **kwargs):
        # Enforce singleton pattern
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Convenience method to get the singleton instance
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
