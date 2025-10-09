from django.db import models


class MovieGenre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='movies/', blank=True, null=True)
    genres = models.ManyToManyField(MovieGenre, related_name='movies')

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


    def __str__(self):
        return self.title

