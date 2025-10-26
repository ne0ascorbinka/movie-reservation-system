from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, datetime, time
from movies.models import Movie, MovieGenre, Hall, Showtime


class Command(BaseCommand):
    help = "Створює тестові фільми, жанри та сеанси"

    def handle(self, *args, **kwargs):
        # --- ЖАНРИ ---
        genres = {name: MovieGenre.objects.get_or_create(name=name)[0] for name in ["Екшн", "Комедія", "Драма"]}

        # --- ФІЛЬМИ ---
        movies_data = [
            {
                "title": "Велика Пригода",
                "duration_minutes": 120,
                "genres": ["Екшн"],
                "poster_url": "https://cdn.prod.website-files.com/687e8d1b96312cc631cafec7/68c48d141e8381607486e3fb_66a4263d01a185d5ea22eeec_6408f6e7b5811271dc883aa8_batman-min.png",
                "description": "У Готемі знову з'являється новий таємничий злодій. На місці злочину він залишає послання для Бетмена. Поліція не може самостійно вести розслідування, тому доводиться в черговий раз звертатися до похмурого героя. Брюса Вейна турбує те, що йому зрозумілі і близькі мотиви лиходія. Він прагне вивести на чисту воду всіх людей, які перебувають при владі і які загрузли в брехні. Вони прикриваються благими намірами і добрими вчинками, але в дійсності їх цікавлять тільки влада і гроші. Бетмен сам не раз стикався з тим, що в багатьох бідах міста винні саме люди, які перебувають при владі, які є невід'ємною частиною злочинного світу.",
            },
            {
                "title": "Смішні Дні",
                "duration_minutes": 95,
                "genres": ["Комедія"],
                "poster_url": "https://assets.mubicdn.net/images/notebook/post_images/19893/images-w1400.jpg?1449196747",
                "description": "Завдяки революційній новій технології, яка розблоковує генетичні спогади, що містяться в ДНК, Каллум Лінч подорожує в минуле. Опинившись в Іспанії 15 століття, він проживає пригоди свого далекого родича Аґілара де Нерха — члена секретного ордена асасинів, який всіма силами захищає вільну волю від властолюбного Ордена Тамплієрів. Назавжди змінений своїм досвідом перебування в минулому, Каллум повертається в сьогодення, де починає боротися з агресією тамплієрів з використанням своїх неймовірних нових знань і навичок.",
            },
            {
                "title": "Дім Мрій",
                "duration_minutes": 105,
                "genres": ["Драма"],
                "poster_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEmHN3GJj5FwwdXGRGgcobyHeF41NDMJyo7w&s",
                "description": "У розпал Другої світової війни полковник США Леслі Гровс призначає блискучого фізика-теоретика Роберта Оппенгеймера науковим керівником Манхеттенського проєкту. Вся індустріальна міць та інноваційні технології країни йдуть на те, щоб випередити нацистську Німеччину у створенні зброї масового знищення на основі розщеплення ядра атома. Оппенгеймер проводить успішні випробування першої у світі ядерної бомби, що дозволяє наблизити перемогу у війні. Проте чоловіка мучать докори совісті, оскільки його винахід здатний призвести до знищення всього людства...",
            },
        ]

        # --- ЗАЛИ ---
        halls = [
            Hall.objects.get_or_create(
                name="Зал 1",
                defaults={"rows": 10, "seats_per_row": 10}
            )[0],
            Hall.objects.get_or_create(
                name="Зал 2",
                defaults={"rows": 8, "seats_per_row": 10}
            )[0],
        ]
# --- СТВОРЕННЯ ФІЛЬМІВ ---
        for m in movies_data:
            movie, _ = Movie.objects.get_or_create(
                title=m["title"],
                defaults={
                    "duration_minutes": m["duration_minutes"],
                    "poster_url": m["poster_url"],
                    "description": m["description"],
                },
            )
            # Оновлюємо якщо фільм існує
            movie.poster_url = m["poster_url"]
            movie.description = m["description"]
            movie.duration_minutes = m["duration_minutes"]
            movie.save()
            movie.genres.set([genres[g] for g in m["genres"]])

               # --- СТВОРЕННЯ СЕАНСІВ ---
        now = timezone.localtime(timezone.now()).replace(hour=10, minute=0, second=0, microsecond=0)

        # 9 сеансів на день (по 3 на фільм, усі в різний час)
        # Крок між сеансами — 1.5 години
        show_hours = [10, 11, 13, 14, 16, 17, 19, 20, 22]  

        all_movies = list(Movie.objects.all())
        movie_count = len(all_movies)

        for day_offset in range(5):
            day = now + timedelta(days=day_offset)

            # індекс для чергування залів
            hall_index = 0
            hour_index = 0

            for movie in all_movies:
                for i in range(3):  # 3 сеанси для кожного фільму
                    if hour_index >= len(show_hours):
                        break  # на випадок, якщо годин менше, ніж потрібно
                    
                    hall = halls[hall_index % len(halls)]
                    hour = show_hours[hour_index]
                    start = timezone.make_aware(datetime.combine(day.date(), time(hour, 0)))

                    Showtime.objects.get_or_create(
                        movie=movie,
                        hall=hall,
                        start_time=start,
                        defaults={"price": 150.00},
                    )

                    # Чергуємо зали і наступний час
                    hall_index += 1
                    hour_index += 1


        self.stdout.write(self.style.SUCCESS("✅ Дані кінотеатру створено"))