from django.shortcuts import render
from django.views.generic import ListView
from movies.models import Movie
# Create your views here.
class MovieListView(ListView):
    model = Movie
    template_name = "movie_list.html"

