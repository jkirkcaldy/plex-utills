from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.views.generic import CreateView
from django.contrib.auth import logout
from .forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView



from .models import Plex
from .tasks import posters4k

# Create your views here.
def index(request):
    plex = Plex.objects.filter(pk=1)
    context = {
         'plex': plex,
         'version': '23.03'
    }
    return render(request, 'app/index.html', context)


def search(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def config(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def config_options(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def run_scripts(request):
    posters4k(None, None)
    return HttpResponse("Hello, world. You're at the polls index.")
def script_logs(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def application_logs(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def help(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def get_films(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def get_shows(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def get_db_films(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def get_db_shows(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def get_db_seasons(request):
    return HttpResponse("Hello, world. You're at the polls index.")
def get_db_episodes(request):
    return HttpResponse("Hello, world. You're at the polls index.")


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