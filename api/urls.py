from django.urls import path, re_path
from api import views

app_name = "api"

urlpatterns = [
    
    # scripts
    path('posters4k/<path:posterVar>', views.Posters4k, name='posters4k'),
    path('posters4k', views.Posters4k, name='posters4k'),
    path('tvposters4k', views.tvposters4k, name='tvposters4k'),
    path('tvseason_showposters', views.tvseason_showposters, name='tvseason_showposters'),
    path('posters3d', views.posters3d, name='posters3d'),
    path('hide4k', views.Posters4k, name='hide4k'),
    path('spoilers', views.spoilerscript, name='spoilers'),
    
    path('task/<path:taskID>', views.runTask, name='task'),
    
    path('autocollections', views.Posters4k, name='autocollections'),
    path('tvspoilers', views.Posters4k, name='tvspoilers'),
    
    path('restore_from_database', views.restore_from_database, name='restore_from_database'),
    path('tmdbRestore', views.runTmdbRestore, name='tmdbRestore'),
    path('tmdbTvRestore', views.runTmdbTvRestore, name='tmdbTVRestore'),
    
    path('logs', views.Logs, name='logs'),
    path('getTaskLogs', views.getTaskLogs, name='getTaskLogs'),    
    path('getSystemLogs', views.getSystemLogs, name='getSystemLogs'),
    path('getNginxAccessLogs', views.getNginxAccessLogs, name='getNginxAccessLogs'),
    path('getNginxErrorLogs', views.getNginxErrorLogs, name='getNginxErrorLogs'),
    path('delete_database/<path:var>', views.delete_database, name='delete_database'),
    
    path('get_db_films', views.get_db_films, name='get_db_films'),
    path('get_db_episodes', views.get_db_episodes, name='get_db_episodes'),
    path('get_db_seasons', views.get_db_seasons, name='get_db_seasons'),    
    path('get_db_shows', views.get_db_shows, name='get_db_shows'),    


    path('reprocess_episode/<path:var>', views.get_db_episodes, name='reprocess_episode'),
    path('delete_episode/<path:var>', views.get_db_episodes, name='delete_episode'),

    path('reprocess_season/<path:var>', views.get_db_seasons, name='reprocess_season'),
    path('delete_season/<path:var>', views.get_db_seasons, name='delete_season'),   

    path('reprocess_show/<path:var>', views.get_db_shows, name='reprocess_show'),
    path('delete_show/<path:var>', views.get_db_shows, name='delete_show'), 

    path('search', views.searchResults, name='search'),
    path('upload', views.upload, name='upload'),
    path('spoiler_webhook', views.spoiler_webhook, name='spoiler_webhook'),
    
    path('updateTasks', views.updateTasks, name='updateTasks'),
    
]
