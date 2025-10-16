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
        self.url = reverse("movies:list")

    def test_movie_list_view_returns_all_movies(self):
        """Basic behaviour: the view should return all existing movies."""
        m1 = Movie.objects.create(title="Movie A")
        m2 = Movie.objects.create(title="Movie B")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movie_list.html")
        # Compare by titles for readability
        movie_titles = [m.title for m in response.context["movie_list"]]
        self.assertCountEqual(movie_titles, [m1.title, m2.title])

    def test_movie_list_view_handles_empty_state(self):
        """Empty state: the view should return 200 and empty movie list."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["movie_list"], [])

    def test_movie_list_ordering_by_created_at_desc(self):
        """Movies should be ordered by descending creation date (newest first)."""
        base_time = timezone.now()

        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = base_time - timedelta(hours=1)
            older = Movie.objects.create(title="Old Movie")

            mock_now.return_value = base_time
            newer = Movie.objects.create(title="New Movie")


        response = self.client.get(self.url)
        movie_list = list(response.context["movie_list"])
        print(older.created_at, newer.created_at)
        self.assertEqual(movie_list[0], newer)
        self.assertEqual(movie_list[1], older)


    def test_movie_list_db_query_efficiency(self):
        """Performance: ensure the list view doesn’t hit DB excessively."""
        Movie.objects.create(title="PerfTest")

        # We expect this simple view to execute few queries (e.g., 1–2 max)
        # Adjust the number if your view uses annotations, select_related, etc.
        with self.assertNumQueriesLessThan(3):
            self.client.get(self.url)
