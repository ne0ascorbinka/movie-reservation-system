from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserLoginForm

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')


def terms(request):
    return render(request, 'terms.html')


def privacy(request):
    return render(request, 'privacy.html')


class UserLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = UserLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('movies:upcoming_showtimes')
