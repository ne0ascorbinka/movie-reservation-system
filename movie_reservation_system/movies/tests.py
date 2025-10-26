from contextlib import contextmanager
from datetime import timedelta
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from unittest.mock import patch

from movies.models import Movie
from movies.models import MovieGenre


class MoviesTest(TestCase):
    def test_create_mymodel_instance(self):
        instance = Movie.objects.create(title="Test Name",
                                        description="Some Description")

        self.assertEqual(Movie.objects.count(), 1)
        self.assertEqual(instance.title, "Test Name")
        self.assertEqual(instance.description, "Some Description")

    def test_mymodel_string_representation(self):
        instance = Movie.objects.create(title="Another Test")
        self.assertEqual(str(instance), "Another Test")

class MoviesGenreTest(TestCase):
    def test_create_mymodel_instance(self):
        instance = MovieGenre.objects.create(name="Test Name")

        self.assertEqual(MovieGenre.objects.count(), 1)
        self.assertEqual(instance.name, "Test Name")

    def test_mymodel_string_representation(self):
        instance = Movie.objects.create(title="Another Test")
        self.assertEqual(str(instance), "Another Test")


class MovieListViewTests(TestCase):
    @contextmanager
    def assertNumQueriesLessThan(self, n):
        with CaptureQueriesContext(connection) as ctx:
            yield
        if len(ctx) >= n:
            self.fail(f"{len(ctx)} queries executed, expected < {n}")

    def setUp(self):
        # We’ll reuse this URL name — adjust if you used something else
        self.url = reverse("movies:movie_list")

    def test_movie_list_view_returns_all_movies(self):
        """Basic behaviour: the view should return all existing movies."""
        m1 = Movie.objects.create(title="Movie A")
        m2 = Movie.objects.create(title="Movie B")

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movies/movie_list.html")
        # Compare by titles for readability
        movie_titles = [m.title for m in response.context["movies"]]
        self.assertCountEqual(movie_titles, [m1.title, m2.title])

    def test_movie_list_view_handles_empty_state(self):
        """Empty state: the view should return 200 and empty movie list."""
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["movies"], [])

    def test_movie_list_ordering_by_created_at_desc(self):
        """Movies should be ordered by descending creation date (newest first)."""
        base_time = timezone.now()

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = base_time - timedelta(hours=1)
            older = Movie.objects.create(title="Old Movie")

            mock_now.return_value = base_time
            newer = Movie.objects.create(title="New Movie")


        response = self.client.get(self.url, follow=True)
        movie_list = list(response.context["movies"])
        self.assertEqual(movie_list[0], newer)
        self.assertEqual(movie_list[1], older)


    def test_movie_list_db_query_efficiency(self):
        """Performance: ensure the list view doesn't hit DB excessively (N+1 problem)."""
        # Create multiple genres
        action = MovieGenre.objects.create(name="Action")
        comedy = MovieGenre.objects.create(name="Comedy")
        drama = MovieGenre.objects.create(name="Drama")
        scifi = MovieGenre.objects.create(name="Sci-Fi")
        
        # Create multiple movies with various genre combinations
        movie1 = Movie.objects.create(title="Action Movie")
        movie1.genres.add(action, drama)
        
        movie2 = Movie.objects.create(title="Comedy Movie")
        movie2.genres.add(comedy)
        
        movie3 = Movie.objects.create(title="Sci-Fi Epic")
        movie3.genres.add(scifi, action, drama)
        
        movie4 = Movie.objects.create(title="Pure Drama")
        movie4.genres.add(drama)
        
        movie5 = Movie.objects.create(title="Multi-Genre")
        movie5.genres.add(action, comedy, drama, scifi)
        
        # If the view accesses genres without prefetch_related, it will cause:
        # 1 query for movies + N queries for genres (one per movie) = 6 queries
        # With proper optimization (prefetch_related('genres')), it should be:
        # 1 query for movies + 1 query for genres = 2 queries
        # Allow 1 extra for potential session/auth queries
        with self.assertNumQueriesLessThan(4):
            response = self.client.get(self.url, follow=True)
        
        # Verify we actually got all movies
        self.assertEqual(len(response.context["movies"]), 5)


    def test_movie_list_no_n_plus_one_with_genres(self):
        """Ensure accessing movie genres in template doesn't cause N+1 queries."""
        # Create test data
        genres = [MovieGenre.objects.create(name=f"Genre {i}") for i in range(3)]
        
        for i in range(10):  # Create 10 movies to make N+1 obvious
            movie = Movie.objects.create(title=f"Movie {i}")
            movie.genres.set(genres)  # Each movie has all genres
        
        # Without prefetch_related('genres'): 1 + 10 = 11 queries
        # With prefetch_related('genres'): 1 + 1 = 2 queries
        # Allow a small buffer for session/middleware queries
        with self.assertNumQueriesLessThan(5):
            response = self.client.get(self.url, follow=True)
            
            # Simulate template accessing genres (this triggers the queries)
            movie_list = response.context["movies"]
            for movie in movie_list:
                list(movie.genres.all())  # Force evaluation like template would


    def test_movie_list_scales_with_data_volume(self):
        """Query count should not scale linearly with number of movies."""
        # Create 20 movies with genres
        genres = [MovieGenre.objects.create(name=f"Genre {i}") for i in range(5)]
        
        for i in range(20):
            movie = Movie.objects.create(title=f"Movie {i}")
            movie.genres.set(genres[:i % 3 + 1])  # Varying number of genres
        
        # Query count should remain constant regardless of movie count
        # Expected: ~2-3 queries (movies + genres + maybe session)
        with self.assertNumQueriesLessThan(5):
            self.client.get(self.url, follow=True)
