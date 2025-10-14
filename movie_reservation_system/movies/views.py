from django.shortcuts import render

from django.utils import timezone
from datetime import timedelta, datetime, date
from .models import Showtime

def upcoming_showtimes(request, date_str=None):
    """
    Показує найближчі сеанси — фільми, що йдуть сьогодні або у вибраний день.
    """
    now = timezone.localtime(timezone.now())
    start_day = now.date()
    days_to_show = 7
    days = [start_day + timedelta(days=i) for i in range(days_to_show)]

    # Якщо користувач вибрав конкретну дату
    if date_str:
        try:
            selected_date = date.fromisoformat(date_str)
        except Exception:
            selected_date = start_day
    else:
        selected_date = start_day

    # Межі дня (00:00 – 23:59)
    day_start = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
    day_end = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))

    # Отримуємо сеанси на цю дату
    showtimes_qs = (
        Showtime.objects
        .select_related('movie', 'hall')
        .filter(start_time__range=(day_start, day_end))
        .order_by('start_time')
    )

    context = {
        "days": days,
        "selected_date": selected_date,
        "showtimes": showtimes_qs,
        "now": now,
    }
    return render(request, "movies/upcoming_showtimes.html", context)
