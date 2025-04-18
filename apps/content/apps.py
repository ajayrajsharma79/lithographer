from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.content'

    def ready(self):
        # Import and connect signals (assuming signals are in apps.webhooks)
        import apps.webhooks.signals
