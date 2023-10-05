import os
from .base import *
import environ

env = environ.Env()
#environ.Env.read_env('/config/.env')
env.read_env(env.str('ENV_PATH', '/config/.env'))

DEBUG = True

SECRET_KEY = env('SECRET_KEY')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'django_db.sqlite3',
    }
}
DATA_UPLOAD_MAX_NUMBER_FIELDS=2000

CELERY_BROKER_URL = env('REDIS_HOST') 
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

SECURE_CROSS_ORIGIN_OPENER_POLICY = 'none'

EMAIL_HOST = env('EMAIL_HOST') 
EMAIL_PORT = env('EMAIL_PORT') 
EMAIL_USE_TLS = env('EMAIL_USE_TLS') 
EMAIL_HOST_USER = env('EMAIL_HOST_USER') 
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD') 
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') 

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}





MEDIA_URL = '/media/'
MEDIA_ROOT = '/config'
#os.path.join(BASE_DIR, 'mediafiles')

MEDIAFILES_DIRS = (
    os.path.join('/config', 'backup'),
    os.path.join('/config', 'backup/film'),
    os.path.join('/config', 'backup/episode'),
    os.path.join('/config', 'backup/season'),
    os.path.join('/config', 'backup/show'),
)
