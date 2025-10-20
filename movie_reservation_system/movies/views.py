from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.views.generic import ListView
from .azure_sas import generate_azure_read_sas_url
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

        for movie in context["movies"]:
            if movie.image:
                movie.poster_url = generate_azure_read_sas_url(movie.image.name)
            else:
                movie.poster_url = None

        return context