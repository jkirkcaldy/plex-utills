from django.urls import path
from api import api
from posters import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    
    # config
    #path('config', views.config, name='config'),
    #path('config_options', views.config_options, name='config_options'),
    # scripts
    path('run_scripts', views.run_scripts, name='run_scripts'),


    
    path('help', api.help, name='help'),
    path('get_films', views.get_films, name='get_films'),
    path('get_shows', views.get_shows, name='get_shows'),
    path('get_seasons', views.get_seasons, name='get_seasons'),
    path('get_episodes', views.get_episodes, name='get_episodes'),
    
    path('get_plex_films', views.get_plex_films, name='get_plex_films'),
    path('get_plex_shows', views.get_plex_shows, name='get_plex_shows'),
    path('get_plex_seasons/<path:guid>', views.get_plex_seasons, name='get_plex_seasons'),
    path('get_plex_episodes/<path:guid>', views.get_plex_episodes, name='get_plex_episodes'),

    
    # Database

    path('reprocess_film/<path:var>', views.help, name='reprocess_film'),
    path('delete_film/<path:var>', views.help, name='delete_film'),
    

    path('info/<path:var>', views.info, name='info'),
    



    # Authentication
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', views.logout_view, name='logout'),    

    path('auth/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('auth/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='auth/auth-password-change-done.html'
    ), name="password_change_done"),    
    path('auth/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('auth/password-reset-confirm/<uidb64>/<token>/', views.UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"
    ),
    path('auth/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
      template_name='auth/auth-password-reset-done.html'
    ), name='password_reset_done'),
    path('auth/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
      template_name='auth/auth-password-reset-complete.html'
    ), name='password_reset_complete'), 
]