from .base import *

DEBUG = False

# Tests run against PostgreSQL + PostGIS test database natively
DATABASES['default']['TEST'] = {
    'NAME': env('TEST_DATABASE_NAME', default='tradeflow_test_db'),
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
