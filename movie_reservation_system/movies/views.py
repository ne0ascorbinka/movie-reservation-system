from datetime import timedelta, datetime, date
from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.utils import timezone

from .azure_sas import generate_azure_read_sas_url
from .models import Movie, Showtime, MovieGenre


class MovieListView(ListView):
    model = Movie
    template_name = "movie_list.html"
    context_object_name = "movies"

    def get_queryset(self):
        """
        Return all movies ordered by newest first,
        with genres prefetched to avoid N+1 queries.
        """
        return (
            Movie.objects
            .select_related()  # No FK to follow, but safe to include
            .prefetch_related("genres")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        """Add SAS URLs to each movie"""
        context = super().get_context_data(**kwargs)

        if not settings.USE_AZURE_STORAGE == True:
            return context

        else:
            for movie in context["movies"]:
                if movie.image:
                    movie.poster_url = generate_azure_read_sas_url(movie.image.name)
                else:
                    movie.poster_url = None

        return context


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




from django.utils import timezone

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
        'now': timezone.now(),
        'genre_filter': genre_filter,
        'search_query': search_query,
    }
    return render(request, "movies/movie_list.html", context)



def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # Дні для вибору у випадаючому списку (сьогодні + наступні 6 днів)
    now = timezone.localtime(timezone.now())
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