from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ecommerce'
    
    def ready(self):
        import apps.ecommerce.signals  # Import the signals module to ensure signal handlers are registered