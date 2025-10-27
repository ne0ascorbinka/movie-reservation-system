from django.views.generic import TemplateView
from django.urls import path
from .views import RegisterView, terms, privacy, UserLoginView, UserLogoutView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('terms/', terms, name='terms'),
    path('privacy/', privacy, name='privacy'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]