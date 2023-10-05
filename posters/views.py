from django.shortcuts import render, redirect
from plexapi.server import PlexServer
from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.auth import logout
from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .models import film, episode
from utils.models import Plex
from .tasks import *
import logging, json, re
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule

from api import views as API

logger = logging.getLogger(__name__)
version = '23.10'

poster_url_base = 'https://www.themoviedb.org/t/p/original'

# Create your views here.
def index(request):
    plex = Plex.objects.filter(pk=1)
    tasks = PeriodicTask.objects.filter(enabled=True)
    context = {
         'plex': plex,
         'tasks': tasks,
         'version': '23.10'
    }
    return render(request, 'app/index.html', context)


def run_scripts(request):
    tasks = PeriodicTask.objects.all()

        
    context = {
         'version': version,
         'tasks':tasks
    }
    return render(request, 'app/scripts.html', context)


def help(request):
    return HttpResponse("Hello, world. You're at the polls index.")
  
def get_plex_films(request):
    films = json.loads(API.get_film_posters())
    p = Paginator(films['films'], 24)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj, 'section': 'film'}
    return render(request, 'app/plex_library.html', context)

def get_plex_shows(request): 
    shows = json.loads(API.get_show_posters())
    p = Paginator(shows['shows'], 24)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj, 'section': 'show'}
    return render(request, 'app/plex_library.html', context)

def get_plex_seasons(request, guid):
    showguid = re.sub('/get_plex_seasons/', '', request.path)
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    lib = config.tvlibrary.split(',')
    for l in lib:
        show = [s for s in plex.library.section(l).search(libtype='show', guid=showguid, limit=1)][0]
    seasons = json.loads(API.get_season_posters(guid))
    p = Paginator(seasons['seasons'], 24)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj, 'section':'season', 'item':show}
    return render(request, 'app/plex_library.html', context)

def get_plex_episodes(request, guid):
    seasonguid = re.sub('/get_plex_episodes/', '', request.path)
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    lib = config.tvlibrary.split(',')
    for l in lib:
        season = [s for s in plex.library.section(l).search(libtype='season', guid=seasonguid, limit=1)][0]
    episodes = json.loads(API.get_episode_posters(guid))
    p = Paginator(episodes['episodes'], 24)
    page_number = request.GET.get('page')
    try:
        page_obj = p.get_page(page_number)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    context = {'page_obj': page_obj, 'section': 'episode', 'item': season}
    return render(request, 'app/plex_library.html', context)

def info(request, var):
    config = Plex.objects.get(pk=1)
    plex = PlexServer(config.plexurl, config.token)
    if 'movie' in var:
        lib = config.filmslibrary.split(',')
        for l in lib:
            item = [s for s in plex.library.section(l).search(guid=var, limit=1)][0]        
        posters = API.get_tmdb_film_posters(var) 
        dbitem = film.objects.filter(guid=var).first()
    elif 'show' in var:
        lib = config.tvlibrary.split(',')
        for l in lib:
            item = [s for s in plex.library.section(l).search(libtype='show', guid=var, limit=1)][0]        
        dbitem = ''
        posters = API.get_tmdb_show_posters(var)
    elif 'season' in var:
        lib = config.tvlibrary.split(',')
        for l in lib:
            item = [s for s in plex.library.section(l).search(libtype='season', guid=var, limit=1)][0]         
        dbitem = show.objects.filter(guid=var).first()
        posters = API.get_tmdb_season_posters(var)
    elif 'episode' in var:
        lib = config.tvlibrary.split(',')
        for l in lib:
            item = [s for s in plex.library.section(l).search(libtype='episode', guid=var, limit=1)][0]         
        dbitem = episode.objects.filter(guid=var).first()
        posters = API.get_tmdb_episode_posters(var)
    context = {
      'pagetitle': 'Info',
      'guid': var, 
      'dbitem': dbitem, 
      'item': item,
      'poster_url': poster_url_base, 
      'posters': posters, 
      'version': version
    }  
    logger.debug(posters)
    return render(request, 'app/info.html', context)




def get_films(request):
    context = {
         'version': '23.10'
    }
    return render(request, 'db/films.html', context)  
def get_shows(request):
    context = {
         'version': '23.10'
    }
    return render(request, 'db/shows.html', context)  
def get_seasons(request):
    context = {
         'version': '23.10'
    }
    return render(request, 'db/seasons.html', context)  
def get_episodes(request):
    context = {
         'version': '23.10'
    }
    return render(request, 'db/episodes.html', context)  



# Authentication
class UserRegistrationView(CreateView):
  template_name = 'auth/auth-signup.html'
  form_class = RegistrationForm
  success_url = '/auth/login/'

class UserLoginView(LoginView):
  template_name = 'auth/auth-signin.html'
  form_class = LoginForm

class UserPasswordResetView(PasswordResetView):
  template_name = 'auth/auth-reset-password.html'
  form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
  template_name = 'auth/auth-password-reset-confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'auth/auth-change-password.html'
  form_class = UserPasswordChangeForm

def logout_view(request):
  logout(request)
  return redirect('/auth/login/')

