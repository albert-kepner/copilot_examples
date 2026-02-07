from django.contrib import admin

from .models import Hobby


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "date_updated")
    search_fields = ("name", "category", "notes")
