# django_celery/celery.py

import os
from celery import Celery
from celery.schedules import crontab
from celery import current_app
import environ

env = environ.Env()

env.read_env(env.str('ENV_PATH', '/config/.env'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plex-utils.settings")
app = Celery("plex_utils")
app.config_from_object("django.conf:settings", namespace="CELERY")


app.autodiscover_tasks()
task = app.task

tasks = current_app.tasks.keys()