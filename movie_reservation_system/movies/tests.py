from django.test import TestCase
from movies.models import Movie
from movies.models import MovieGenre
# Create your tests here.

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
        instance = MovieGenre.objects.create(headline="Test Name")

        self.assertEqual(MovieGenre.objects.count(), 1)
        self.assertEqual(instance.headline, "Test Name")

    def test_mymodel_string_representation(self):
        instance = Movie.objects.create(title="Another Test")
        self.assertEqual(str(instance), "Another Test")