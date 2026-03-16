from django.contrib import admin

from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'year', 'genre', 'status')
    list_filter = ('status', 'genre')
    search_fields = ('title', 'director')
