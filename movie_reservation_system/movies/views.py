from datetime import timedelta, datetime, date
from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView
from django.utils import timezone

from .azure_sas import generate_azure_read_sas_url
from .models import Showtime
from .models import Movie


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
    """
    Показує найближчі сеанси — фільми, що йдуть сьогодні або у вибраний день.
    """
    now = timezone.localtime(timezone.now())
    start_day = now.date()
    days_to_show = 7
    days = [start_day + timedelta(days=i) for i in range(days_to_show)]

    # Якщо користувач вибрав конкретну дату
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
        except Exception:
            selected_date = start_day
    else:
        selected_date = start_day

    # Межі дня (00:00 – 23:59)
    day_start = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))

    # Отримуємо сеанси на цю дату
    showtimes_qs = (
        Showtime.objects
        .select_related('movie', 'hall')
        .filter(start_time__range=(day_start, day_end))
        .order_by('start_time')
    )

    context = {
        "days": days,
        "selected_date": selected_date,
        "showtimes": showtimes_qs,
        "now": now,
    }
    return render(request, "movies/upcoming_showtimes.html", context)
