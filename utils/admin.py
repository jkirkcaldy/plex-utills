from django.contrib import admin

# Register your models here.
from .models import Plex, advancedSettings

class PlexAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['plexurl', 'filmslibrary', 'tvlibrary']
    #fields = ['plexurl', token, filmslibrary, tvlibrary, library3d, tautulli_server, tautulli_api, tmdb_api, tmdb_restore, backup, posters4k, miniposters, hdr, audio_posters, posters3d]

class advancedAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['mountedpath', 'manualplexpath', 'manualplexpathfield']
    #fields = ['plexurl', token, filmslibrary, tvlibrary, library3d, tautulli_server, tautulli_api, tmdb_api, tmdb_restore, backup, posters4k, miniposters, hdr, audio_posters, posters3d]


admin.site.register(Plex, PlexAdmin)
admin.site.register(advancedSettings, advancedAdmin)

def get_app_list(self, request):
    """
    Return a sorted list of all the installed apps that have been
    registered in this site.
    """
    # Retrieve the original list
    app_dict = self._build_app_dict(request)
    app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

    # Sort the models customably within each app.
    for app in app_list:
        if app['app_label'] == 'utils':
            ordering = {
                'Config': 1,
                'Advanced Settings': 2
            }
            app['models'].sort(key=lambda x: ordering[x['name']])

    return app_list

admin.AdminSite.get_app_list = get_app_list