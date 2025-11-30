from django.views.generic import TemplateView
from django.urls import path
from .views import RegisterView, TermsView, PrivacyView, UserLoginView, UserLogoutView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]