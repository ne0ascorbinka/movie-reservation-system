from django.contrib import admin
from .models import MovieGenre, Movie, Hall, Showtime

# Register your models here.



@admin.register(MovieGenre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes')
    search_fields = ('title',)



@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'price', 'created_at')
    list_filter = ('hall', 'start_time', 'movie')
    search_fields = ('movie__title',)
    
@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_per_row", "total_seats")

    def total_seats(self, obj):
        return obj.rows * obj.seats_per_row
    total_seats.short_description = "Всього місць"


