import os

from django.apps import AppConfig

class PostApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'post_api'
    def ready(self):
        if os.environ.get("RUN_MAIN", None) != 'true':
            from app_scheduler import timer
            timer.start()