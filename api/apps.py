from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    def ready(self):
        from django.contrib.sites.models import Site
        from django.conf import settings
        site = Site.objects.get(pk=1)
        site.domain = settings.DOMAIN
        site.name = settings.DOMAIN
        site.save()