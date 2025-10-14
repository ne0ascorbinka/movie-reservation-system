from django.db import models
from django.utils import timezone


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
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    poster_url = models.URLField(blank=True) 
    genres = models.ManyToManyField(MovieGenre, related_name='movies')

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


    def __str__(self):
        return self.title

class Hall(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name='showtimes')
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=7, decimal_places=2, default=120.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['movie']),
        ]

    def __str__(self):
        return f"{self.movie.title} — {self.start_time.strftime('%Y-%m-%d %H:%M')} ({self.hall.name})"

    @property
    def is_upcoming(self):
        return self.start_time >= timezone.now()
