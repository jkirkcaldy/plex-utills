from django.contrib import admin

# Register your models here.
from posters.models import *

class FilmAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['title', 'res', 'hdr', 'audio', 'checked']

class EpisodeAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title', 'res', 'hdr', 'audio', 'checked']
    
class SeasonAdmin(admin.ModelAdmin):
    search_fields = ['title', 'guid']
    list_display = ['title', 'hdr', 'res', 'checked']
    
class ShowAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['title', 'checked']

admin.site.register(film, FilmAdmin)
admin.site.register(episode, EpisodeAdmin)
admin.site.register(season, SeasonAdmin)
admin.site.register(show, ShowAdmin)