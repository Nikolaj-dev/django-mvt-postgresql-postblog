from django.apps import AppConfig


class PostappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PostApp'

    def ready(self):
        from . import signals

