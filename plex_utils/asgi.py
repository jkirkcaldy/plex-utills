import os
import environ


env = environ.Env()

env.read_env(env.str('ENV_PATH', '/config/.env'))

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plex_utils.settings')

application = get_asgi_application()
