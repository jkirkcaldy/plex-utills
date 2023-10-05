import os
from .base import *
import environ

env = environ.Env()
#environ.Env.read_env('/config/.env')
env.read_env(env.str('ENV_PATH', '/config/.env'))

DEBUG = False

SECRET_KEY = env('SECRET_KEY')


DATABASES = {
    'default': {
        'ENGINE': env('SQL_ENGINE'),
        'NAME': env('SQL_DATABASE'),
        'USER': env('SQL_USER'),
        'PASSWORD': env('SQL_PASSWORD'),
        'HOST': env('SQL_HOST'),
        'PORT': env('SQL_PORT'),
    }
}
DATA_UPLOAD_MAX_NUMBER_FIELDS=2000

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env('REDIS_HOST'),
    }
}

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True
#
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'none' #'same-origin'
#
#SECURE_HSTS_PRELOAD = True
#
#SECURE_HSTS_SECONDS = 600

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CELERY_BROKER_URL = env('REDIS_HOST')

EMAIL_HOST = env('EMAIL_HOST') 
EMAIL_PORT = env('EMAIL_PORT') 
EMAIL_USE_TLS = env('EMAIL_USE_TLS') 
EMAIL_HOST_USER = env('EMAIL_HOST_USER') 
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD') 
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL') 


CELERY_BROKER_URL = env('REDIS_HOST')
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


MEDIA_URL = '/media/'
MEDIA_ROOT = '/config/backup'
#os.path.join(BASE_DIR, 'mediafiles')

MEDIAFILES_DIRS = (
    os.path.join(BASE_DIR, 'mediafiles'),
)
