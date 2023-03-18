from django.contrib import admin

# Register your models here.
from .models import Plex, film, episode, season

admin.site.register(Plex)
admin.site.register(film)
admin.site.register(episode)
admin.site.register(season)