from django.apps import AppConfig
import os

class UtilsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utils'
    def ready(self):
        from utils.models import Plex, advancedSettings
        from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule
        import datetime
        Plex.objects.get_or_create(
            pk=1,
        )
        advancedSettings.objects.get_or_create(
            pk=1,
        )
        midnight = CrontabSchedule.objects.filter(minute=0, hour=0, timezone='Europe/London')
        if not midnight:
            CrontabSchedule.objects.create(
                minute=0,
                hour=0,
                timezone='Europe/London'
            )
        midnight_schedule = CrontabSchedule.objects.filter(minute=0, hour=0, timezone='Europe/London')[0]
        try:
            PeriodicTask.objects.create(
                name='4K_Posters',
                task='plex-utils.Posters4k',
                crontab = midnight_schedule,
                kwargs = '{"webhooktitle": "","posterVar": "","mediaType":"film"}',
                start_time=datetime.datetime.now(),
                description='Add 4k banners to your Films',
                enabled=False,
            )
        except:
            pass
        try:
            PeriodicTask.objects.create(
                name='TV_4K_Posters',
                task='plex-utils.Posters4kTV',
                crontab = midnight_schedule,
                kwargs = '{"posterVar": "","mediaType":"film"}',
                start_time=datetime.datetime.now(),
                description='Add 4k banners to your TV Shows',
                enabled=False,
            )
        except:
            pass
        try:
            PeriodicTask.objects.create(
                name='Auto_Collections',
                task='plex-utils.autocollections',
                crontab = midnight_schedule,
                start_time=datetime.datetime.now(),
                description='Add some automatica collections to your Films library',
                enabled=False,
            )
        except:
            pass
        try:
            PeriodicTask.objects.create(
                name='spoilers',
                task='plex-utils.spoliers',
                crontab = midnight_schedule,
                kwargs = '{"guid": ""}',
                start_time=datetime.datetime.now(),
                description='Blur Episode posters to avoid spoilers',
                enabled=False,
            )
        except:
            pass
        
        if os.path.exists('/config/app.db'):
            from utils.views import flask2django
            flask2django.delay()