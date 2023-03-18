from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),

    path('search', views.search, name='search'),
    
    # config
    path('config', views.config, name='config'),
    path('config_options', views.config_options, name='config_options'),
    # scripts
    path('run_scripts', views.run_scripts, name='run_scripts'),
    path('script_logs', views.script_logs, name='script_logs'),
    path('application_logs', views.application_logs, name='application_logs'),
    path('help', views.help, name='help'),

    path('get_films', views.get_films, name='get_films'),
    path('get_shows', views.get_shows, name='get_shows'),
    path('get_db_films', views.get_db_films, name='get_db_films'),
    path('get_db_shows', views.get_db_shows, name='get_db_shows'),
    path('get_db_seasons', views.get_db_seasons, name='get_db_seasons'),    
    path('get_db_episodes', views.get_db_episodes, name='get_db_episodes'),    

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