from django.db import models


class MovieGenre(models.Model):
    headline = models.CharField(max_length=100)

    class Meta:
        ordering = ["headline"]

    def __str__(self):
        return self.headline


class Movie(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to=None,
        height_field=None,
        width_field=None,
        max_length=100,
        blank=True
    )
    genres = models.ManyToManyField(MovieGenre, related_name='movies')

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

