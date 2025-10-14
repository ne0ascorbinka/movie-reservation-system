from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.upcoming_showtimes, name="upcoming_showtimes"),
    path("day/<slug:date_str>/", views.upcoming_showtimes, name="showtimes_by_date"),
    path("all/", views.movie_list, name="movie_list"),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),


]
