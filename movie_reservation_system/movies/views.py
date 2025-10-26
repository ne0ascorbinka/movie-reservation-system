from datetime import timedelta, datetime, date
from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.utils import timezone

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


def upcoming_showtimes(request, date_str=None):
    now = timezone.now()+ timedelta(hours=3)
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


def movie_list(request):
    movies = Movie.objects.all().prefetch_related('genres')
    genres = MovieGenre.objects.all()

    # Фільтрація по жанру
    genre_filter = request.GET.get('genre')
    if genre_filter:
        movies = movies.filter(genres__id=genre_filter)

    # Пошук по назві
    search_query = request.GET.get('q')
    if search_query:
        movies = movies.filter(title__icontains=search_query)

    context = {
        'movies': movies.distinct(),
        'genres': genres,
        'now': timezone.now()+ timedelta(hours=3),
        'genre_filter': genre_filter,
        'search_query': search_query,
    }
    return render(request, "movies/movie_list.html", context)



def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # Дні для вибору у випадаючому списку (сьогодні + наступні 6 днів)
    now = (timezone.localtime(timezone.now())+ timedelta(hours=3))
    days = [now + timedelta(days=i) for i in range(7)]

    # Вибрана дата
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = now.date()

    # Showtimes для обраної дати
    showtimes = movie.showtimes.filter(
        start_time__date=selected_date
    ).order_by('start_time')

    context = {
        'movie': movie,
        'days': days,
        'selected_date': selected_date,
        'showtimes': showtimes,
        'now': now,
    }
    return render(request, "movies/movie_detail.html", context)

def booking_detail(request, showtime_id):
    showtime = get_object_or_404(Showtime, id=showtime_id)
    hall = showtime.hall

    # Створюємо список рядів і місць
    seat_rows = []
    rows = [chr(65 + i) for i in range(hall.rows)]  # A, B, C...
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
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")

        for sid in selected_ids:
            seat = Seat.objects.get(id=sid)
            Booking.objects.create(
                showtime=showtime,
                seat=seat,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )

        return redirect("movies:booking_success", showtime_id=showtime.id)

    return render(request, "movies/booking_detail.html", {
        "showtime": showtime,
        "seat_rows": seat_rows
    })
    
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