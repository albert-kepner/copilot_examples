from django.core.exceptions import ValidationError
from django.db import models


class Hobby(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_updated", "-date_created"]

    def __str__(self) -> str:
        return self.name


class HobbyDetail(models.Model):
    hobby = models.ForeignKey(
        Hobby,
        on_delete=models.CASCADE,
        related_name="details",
        db_column="parent_id",
    )
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_updated", "id"]
        db_table = "hobby_details"

    def __str__(self) -> str:
        return self.name or f"Detail {self.pk or ''}".strip()

    def clean(self) -> None:
        super().clean()
        fields = [self.name, self.description, self.category, self.url, self.notes]
        if not any(value and str(value).strip() for value in fields):
            raise ValidationError("Provide at least one detail field.")
