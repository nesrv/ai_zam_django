from django.apps import AppConfig


class ObjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'object'
    
    def ready(self):
        import object.signals
