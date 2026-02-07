from django.contrib import admin

from .models import Hobby, HobbyDetail


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "date_updated")
    search_fields = ("name", "category", "notes")


@admin.register(HobbyDetail)
class HobbyDetailAdmin(admin.ModelAdmin):
    list_display = ("hobby", "name", "category", "date_updated")
    search_fields = ("name", "category", "notes")
