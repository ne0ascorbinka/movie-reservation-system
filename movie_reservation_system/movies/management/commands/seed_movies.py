from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime, time
from movies.models import Movie, MovieGenre, Hall, Showtime

class Command(BaseCommand):
    help = "Створює тестові фільми, жанри та сеанси"

    def handle(self, *args, **kwargs):
        genres = {name: MovieGenre.objects.get_or_create(name=name)[0] for name in ["Action", "Comedy", "Drama"]}
        movies = [
            {"title": "Велика Пригода", "duration_minutes": 120, "genres": ["Action"]},
            {"title": "Смішні Дні", "duration_minutes": 95, "genres": ["Comedy"]},
            {"title": "Дім Мрій", "duration_minutes": 105, "genres": ["Drama"]},
        ]
        halls = [
            Hall.objects.get_or_create(name="Зал 1", defaults={"capacity": 100})[0],
            Hall.objects.get_or_create(name="Зал 2", defaults={"capacity": 80})[0],
        ]

        for m in movies:
            movie, _ = Movie.objects.get_or_create(title=m["title"], defaults={"duration_minutes": m["duration_minutes"]})
            movie.genres.set([genres[g] for g in m["genres"]])

        now = timezone.localtime(timezone.now()).replace(hour=12, minute=0, second=0, microsecond=0)
        for day_offset in range(5):
            day = now + timedelta(days=day_offset)
            for movie in Movie.objects.all():
                for hour in [12, 15, 18]:
                    start = timezone.make_aware(datetime.combine(day.date(), time(hour, 0)))
                    Showtime.objects.get_or_create(
                        movie=movie,
                        hall=halls[day_offset % len(halls)],
                        start_time=start,
                        defaults={"price": 150.00}
                    )
        self.stdout.write(self.style.SUCCESS("✅ Дані кінотеатру створено"))
