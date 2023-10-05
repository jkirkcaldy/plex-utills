from django.db import models

# Create your models here.
class Plex(models.Model):
    # plex and docker config
    plexurl = models.CharField(max_length=200, default='https://app.plex.tv/desktop/#!/')
    token = models.CharField(max_length=200, default='super_secret_token')
    tautulli_server = models.CharField(max_length=200, null=True, blank=True)
    tautulli_api = models.CharField(max_length=200, null=True, blank=True)
    filmslibrary = models.CharField(max_length=200, default='Films')
    tvlibrary = models.CharField(max_length=200, default='TV Shows')
    library3d = models.CharField(max_length=200, null=True, blank=True)
    tmdb_api = models.CharField(max_length=200, null=True, blank=True)
    tmdb_restore = models.BooleanField(default=False)
    backup = models.BooleanField(default=True)
    posters4k = models.BooleanField(default=False)
    miniposters = models.BooleanField(default=False)
    tv4kposters = models.BooleanField(default=False)
    films4kposters = models.BooleanField(default=False)    
    hdr = models.BooleanField(default=False)
    audio_posters = models.BooleanField(default=False)
    tvPosterQuickScan = models.BooleanField(null=False, blank=False, default=True)
    posters3d = models.BooleanField(default=False)
    autocollections = models.BooleanField(default=False)
    disney = models.BooleanField(default=False)
    pixar = models.BooleanField(default=False)
    mcu_collection = models.BooleanField(default=False)
    tr_r_p_collection = models.BooleanField(default=False)
    hide4k = models.BooleanField(default=False)
    transcode = models.BooleanField(default=False)
    recreate_hdr = models.BooleanField(default=False)
    new_hdr = models.BooleanField(default=True)
    default_poster = models.BooleanField(default=False)
    spoilers = models.BooleanField(default=False)    
    skip_media_info = models.BooleanField(default=False)


    class Meta:
        verbose_name_plural = 'Config'

class advancedSettings(models.Model):
    mountedpath = models.CharField(max_length=200, null=True, blank=True, default='/films')    
    manualplexpath = models.BooleanField(default=False)
    manualplexpathfield = models.CharField(max_length=200, null=True, blank=True, default=None)
    class Meta:
        verbose_name_plural = 'Advanced Settings'