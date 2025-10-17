from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.upcoming_showtimes, name="upcoming_showtimes"),
    path("day/<slug:date_str>/", views.upcoming_showtimes, name="showtimes_by_date"),
    path("all/", views.movie_list, name="movie_list"),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path("booking/<int:showtime_id>/", views.booking_detail, name="booking_detail"),
    path("showtime/<int:showtime_id>/success/", views.booking_success, name="booking_success"),



]
