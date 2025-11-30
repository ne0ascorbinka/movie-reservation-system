from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.UpcomingShowtimesView.as_view(), name="upcoming_showtimes"),
    path("day/<slug:date_str>/", views.UpcomingShowtimesView.as_view(), name="showtimes_by_date"),
    path("all/", views.MovieListView.as_view(), name="movie_list"),
    path('<int:movie_id>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path("booking/<int:showtime_id>/", views.BookingDetailView.as_view(), name="booking_detail"),
    path("showtime/<int:showtime_id>/success/", views.booking_success, name="booking_success"),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]
