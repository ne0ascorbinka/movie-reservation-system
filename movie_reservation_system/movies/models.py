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
    rows = models.PositiveIntegerField(default=10)  
    seats_per_row = models.PositiveIntegerField(default=12)  

    def total_seats(self):
        return self.rows * self.seats_per_row

    def __str__(self):
        return f"{self.name} (Рядів: {self.rows}, Місць у ряду: {self.seats_per_row})"

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
    
class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="seats")
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('hall', 'row', 'number')
        ordering = ['row', 'number']

    def __str__(self):
        return f"{self.row}{self.number} ({self.hall.name})"


class Booking(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="bookings")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name="bookings")
    user_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('showtime', 'seat')

    def __str__(self):
        return f"{self.seat} for {self.showtime}"

