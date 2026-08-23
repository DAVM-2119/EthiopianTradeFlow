from django.apps import AppConfig

class SynchronizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.synchronization'
    verbose_name = 'Offline Synchronization'
