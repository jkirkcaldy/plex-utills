from django.db import models
from django.dispatch import receiver
import os
from django.conf import settings

class film(models.Model):
    title = models.CharField(max_length=200)
    guid = models.CharField(max_length=200)
    guids = models.CharField(max_length=200)
    size = models.CharField(max_length=200, null=True, blank=True)
    res = models.CharField(max_length=200, null=True, blank=True)
    hdr = models.CharField(max_length=200, null=True, blank=True)
    audio = models.CharField(max_length=200, null=True, blank=True)
    poster = models.CharField(max_length=256, null=True, blank=True)
    checked = models.BooleanField(null=True, blank=True, default=False)
    bannered_poster = models.CharField(max_length=256, null=True, blank=True)
    url= models.URLField(null=True, blank=True)

class film3d(models.Model):
    title = models.CharField(max_length=200)
    guid = models.CharField(max_length=200)
    guids = models.CharField(max_length=200)
    size = models.CharField(max_length=200, null=True, blank=True)
    poster = models.CharField(max_length=256, null=True, blank=True)
    checked = models.BooleanField(null=True, blank=True, default=False)
    bannered_poster = models.CharField(max_length=256, null=True, blank=True)
    url= models.URLField(null=True, blank=True)


class episode(models.Model):
    title = models.CharField(max_length=200)
    guid = models.CharField(max_length=200, unique=True)
    guids = models.CharField(max_length=200)
    parentguid = models.CharField(max_length=200, null=True)
    grandparentguid = models.CharField(max_length=200, null=True)
    size = models.CharField(max_length=200,null=True, blank=True)
    res = models.CharField(max_length=200, default='unknown')
    hdr = models.CharField(max_length=200, default='none')
    audio = models.CharField(max_length=200, default='unknown')
    poster = models.CharField(max_length=256, null=True, blank=True)
    bannered_poster = models.CharField(max_length=256, null=True, blank=True, default=None)
    checked = models.BooleanField(null=True, blank=True)
    blurred = models.BooleanField(null=True, blank=True, default=False)
    show_season = models.CharField(max_length=200, blank=True, null=True)
    url = models.URLField(null=True, blank=True)
    mtime = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        ordering = ('-title',)
        verbose_name_plural = "Episodes"

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return self.title
    
    def __repr__(self):
        return str(self.guid)    
    
class season(models.Model):
    title = models.CharField(max_length=200)
    guid = models.CharField(max_length=200, unique=True)
    hdr = models.BooleanField(default=False)
    res = models.CharField(max_length=6, default='unknown')
    poster = models.CharField(max_length=256, null=True, blank=True)
    bannered_poster = models.CharField(max_length=256, null=True, blank=True)
    checked = models.BooleanField(null=True, blank=True)
    episodes = models.ManyToManyField(
        episode,
        related_name='episode',
        blank=True
    )
    url = models.URLField(null=True, blank=True)
    class Meta:
        ordering = ('-title',)
        verbose_name_plural = "Seasons"

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return self.title
    
    def __repr__(self):
        return str(self.guid)  
    
class show(models.Model):
    title = models.CharField(max_length=200)
    guid = models.CharField(max_length=200, unique=True)
    hdr = models.BooleanField(default=False)
    res = models.CharField(max_length=6, default='unknown')
    poster = models.CharField(max_length=256, null=True, blank=True)
    bannered_poster = models.CharField(max_length=256, null=True, blank=True)
    checked = models.BooleanField(null=True, blank=True)
    seasons = models.ManyToManyField(
        season,
        related_name='season',
        blank=True
    )
    url = models.URLField(null=True, blank=True)
    class Meta:
        ordering = ('-title',)
        verbose_name_plural = "Shows"

    def __unicode__(self):
        return u'%s' % self.pk

    def __str__(self):
        return self.title
    
    def __repr__(self):
        return str(self.guid)      
    
@receiver(models.signals.post_delete, sender=show)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.poster)))
    if instance.bannered_poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))   ) 
                    
@receiver(models.signals.post_delete, sender=season)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.poster)))
    if instance.bannered_poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster)))
            
@receiver(models.signals.post_delete, sender=episode)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.poster)))
    if instance.bannered_poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))    ) 

@receiver(models.signals.post_delete, sender=film)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.poster)))
    if instance.bannered_poster:
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))):
            os.remove(os.path.join(settings.MEDIA_ROOT, str(instance.bannered_poster))      ) 