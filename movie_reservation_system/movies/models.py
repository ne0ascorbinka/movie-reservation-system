from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

class MovieGenre(models.Model):
    headline = models.CharField(max_length=100)
    movies = models.ManyToManyField(Movie)

    class Meta:
        ordering = ["headline"]

    def __str__(self):
        return self.headline
