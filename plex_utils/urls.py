from django.contrib import admin
from django.urls import path, include
from django.urls import re_path
from plex_utils import views

urlpatterns = [
    re_path(r'^media/(?P<file>.*)$', views.secure, name='protected'),
    path('', include('posters.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path(r'celery-progress/', include('celery_progress.urls')),
]
