from django.views.generic import ListView
from movies.models import Movie


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
