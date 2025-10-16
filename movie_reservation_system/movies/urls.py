from django.urls import path
from .views import MovieListView


app_name = "movies"

urlpatterns = [
    path('', MovieListView.as_view(), name='list'),
]
