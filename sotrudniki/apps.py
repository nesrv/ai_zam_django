from django.apps import AppConfig


class SotrudnikiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sotrudniki"
    
    def ready(self):
        import sotrudniki.signals
