from datetime import timedelta, datetime, date
from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, ListView, TemplateView
from django.utils import timezone
from django.conf import settings
from typing import Any

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .azure_sas import generate_azure_read_sas_url
from .models import Movie, Showtime, MovieGenre, Seat, Booking


class MovieListView(ListView):
    model = Movie
    template_name = "movies/movie_list.html"
    context_object_name = "movies"

    def get_queryset(self):
        """
        Return movies with optional filtering by genre and search query.
        Prefetch genres to avoid N+1 queries.
        """
        queryset = (
            Movie.objects
            .prefetch_related("genres")
            .order_by("-created_at")
        )
        
        # Filter by genre
        genre_filter = self.request.GET.get('genre')
        if genre_filter:
            queryset = queryset.filter(genres__id=genre_filter)
        
        # Search by title
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        
        # Use distinct() to avoid duplicates when filtering by genres
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        """
        Add genres list, current filters, and Azure SAS URLs if needed.
        """
        context = super().get_context_data(**kwargs)
        
        # Add all genres for the filter dropdown
        context['genres'] = MovieGenre.objects.all()
        
        # Add current time (with timezone offset)
        context['now'] = timezone.now() + timedelta(hours=3)
        
        # Preserve filter state for the template
        context['genre_filter'] = self.request.GET.get('genre')
        context['search_query'] = self.request.GET.get('q')
        
        # Add Azure SAS URLs if using Azure storage
        if settings.USE_AZURE_STORAGE:
            for movie in context["movies"]:
                if movie.image:
                    movie.poster_url = generate_azure_read_sas_url(movie.image.name)
                else:
                    movie.poster_url = None
        
        return context


class UpcomingShowtimesView(TemplateView):
    template_name = "movies/upcoming_showtimes.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        now = timezone.now() + timedelta(hours=3)
        date_str = self.kwargs.get('date_str')

        if date_str:
            selected_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            selected_date = now.date()
        
        showtimes = Showtime.objects.filter(
            start_time__date=selected_date
        ).select_related('movie', 'hall').order_by('start_time')

        movies_dict = {}
        for showtime in showtimes:
            movies_dict.setdefault(showtime.movie, []).append(showtime)
        
        days = [now.date() + timezone.timedelta(days=i) for i in range(7)]

        context.update({
            'now': now,
            'days': days,
            'selected_date': selected_date,
            'movies_dict': movies_dict,
        })
        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = "movies/movie_detail.html"
    context_object_name = "movie"
    pk_url_kwarg = "movie_id"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        movie = self.object
        now = timezone.localtime(timezone.now()) + timedelta(hours=3)
        days = [now + timedelta(days=i) for i in range(7)]

        selected_date_str = self.request.GET.get('date')
        if selected_date_str:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = now.date()
        
        showtimes = movie.showtimes.filter(
            start_time__date=selected_date
        ).order_by('start_time')

        context.update(
            {
                'days': days,
                'selected_date': selected_date,
                'showtimes': showtimes,
                'now': now,
            }
        )

        return context
    

from django.contrib.auth.decorators import login_required

@login_required
def booking_detail(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    hall = showtime.hall

    # Формування рядів і місць
    seat_rows = []
    rows = [chr(65 + i) for i in range(hall.rows)]
    for row_letter in rows:
        row_seats = []
        for number in range(1, hall.seats_per_row + 1):
            seat, _ = Seat.objects.get_or_create(hall=hall, row=row_letter, number=number)
            is_occupied = Booking.objects.filter(showtime=showtime, seat=seat).exists()
            row_seats.append({
                "id": seat.id,
                "row": seat.row,
                "number": seat.number,
                "occupied": is_occupied
            })
        seat_rows.append({"row": row_letter, "seats": row_seats})

    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_seats")

        for sid in selected_ids:
            seat = Seat.objects.get(id=sid)
            Booking.objects.create(
                showtime=showtime,
                seat=seat,
                user=request.user  # ✅ нове поле
            )

        return redirect("movies:booking_success", showtime_id=showtime.id)

    return render(request, "movies/booking_detail.html", {
        "showtime": showtime,
        "seat_rows": seat_rows
    })

@login_required
def my_bookings(request):
    # Отримуємо всі бронювання поточного користувача
    bookings = Booking.objects.filter(user=request.user).select_related('showtime', 'seat', 'showtime__movie')
    
    now = timezone.now()
    # Передамо у шаблон інформацію, чи можна скасувати бронювання
    booking_list = []
    for b in bookings:
        can_cancel = b.showtime.start_time > now
        booking_list.append({
            'id': b.id,
            'movie_title': b.showtime.movie.title,
            'showtime': b.showtime.start_time,
            'hall_name': b.showtime.hall.name, 
            'seat': f"{b.seat.row}{b.seat.number}",
            'can_cancel': can_cancel
        })

    return render(request, 'movies/my_bookings.html', {'bookings': booking_list})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.showtime.start_time <= timezone.now():
        messages.warning(request, "Це бронювання вже відбулося, його не можна скасувати.")
    else:
        booking.delete()
        messages.success(request, "Бронювання успішно скасоване.")
    return redirect('movies:my_bookings')

    
def booking_success(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    return render(request, "movies/booking_success.html", {"showtime": showtime})




"""from django.shortcuts import render
from .models import Movie, Showtime
from django.utils import timezone
from django.db.models import Prefetch

def upcoming_showtimes(request, date_str=None):
    now = timezone.now()
    if date_str:
        selected_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = now.date()

    # Вибираємо всі showtimes на певну дату і зв'язуємо з фільмами
    showtimes = Showtime.objects.filter(
        start_time__date=selected_date
    ).select_related('movie', 'hall').order_by('start_time')

    # Створюємо словник: movie -> list of showtimes
    movies_dict = {}
    for s in showtimes:
        if s.movie not in movies_dict:
            movies_dict[s.movie] = []
        movies_dict[s.movie].append(s)

    # Дні для вкладок (поточний день + наступні 6 днів)
    days = [now.date() + timezone.timedelta(days=i) for i in range(7)]

    context = {
        'now': now,
        'days': days,
        'selected_date': selected_date,
        'movies_dict': movies_dict,  # передаємо словник movie → showtimes
    }
    return render(request, "movies/upcoming_showtimes.html", context)
"""