from django.apps import AppConfig


class MediaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.media'

    def ready(self):
        # Import and connect signals (assuming signals are in apps.webhooks)
        import apps.webhooks.signals
