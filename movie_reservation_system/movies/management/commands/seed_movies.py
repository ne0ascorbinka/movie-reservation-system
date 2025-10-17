from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime, time
from movies.models import Movie, MovieGenre, Hall, Showtime

class Command(BaseCommand):
    help = "Створює тестові фільми, жанри та сеанси"

    def handle(self, *args, **kwargs):
        genres = {name: MovieGenre.objects.get_or_create(name=name)[0] for name in ["Action", "Comedy", "Drama"]}
        movies = [
            {"title": "Велика Пригода", "duration_minutes": 120, "genres": ["Action"],"poster_url":"https://cdn.prod.website-files.com/687e8d1b96312cc631cafec7/68c48d141e8381607486e3fb_66a4263d01a185d5ea22eeec_6408f6e7b5811271dc883aa8_batman-min.png","description":"When a sadistic serial killer begins murdering key political figures in Gotham, the Batman is forced to investigate the city's hidden corruption and question his family's involvement."},
            {"title": "Смішні Дні", "duration_minutes": 95, "genres": ["Comedy"],"poster_url":"https://assets.mubicdn.net/images/notebook/post_images/19893/images-w1400.jpg?1449196747","description":"In 8th century China, 10-year-old general's daughter Nie Yinniang is handed over to a nun who initiates her into the martial arts, transforming her into an exceptional assassin charged with eliminating cruel and corrupt local governors. One day, having failed in a task, she is sent back by her mistress to the land of her birth, with orders to kill the man to whom she was betrothed - a cousin who now leads the largest independent military region in North China. After 13 years of exile, the young woman must confront her parents, her memories and her long-repressed feelings."},
            {"title": "Дім Мрій", "duration_minutes": 105, "genres": ["Drama"],"poster_url":"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEmHN3GJj5FwwdXGRGgcobyHeF41NDMJyo7w&s","description":"Reviewers say 'Oppenheimer' by Christopher Nolan is a complex biopic delving into J. Robert Oppenheimer's role in atomic bomb development. Themes of moral dilemmas, scientific responsibility, and nuclear impact are prominent. Cillian Murphy's performance, technical aspects, and historical accuracy receive praise. However, some find the pacing slow, narrative disjointed, and runtime excessive. Critics also note a lack of emotional depth and underdeveloped characters. Despite these issues, Nolan's direction, visual style, and thought-provoking nature are widely appreciated."},
        ]
        halls = [
    Hall.objects.get_or_create(
        name="Зал 1", 
        defaults={"rows": 10, "seats_per_row": 10}  # 10 рядів, по 10 місць
    )[0],
    Hall.objects.get_or_create(
        name="Зал 2", 
        defaults={"rows": 8, "seats_per_row": 10}  # 8 рядів, по 10 місць
    )[0],
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
