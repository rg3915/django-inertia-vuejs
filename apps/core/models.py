from django.db import models


class Movie(models.Model):
    class Status(models.TextChoices):
        WANT = 'want', 'Quero Ver'
        WATCHING = 'watching', 'Assistindo'
        WATCHED = 'watched', 'Assistido'

    title = models.CharField(max_length=200)
    director = models.CharField(max_length=200, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.WANT
    )
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Filme'
        verbose_name_plural = 'Filmes'

    def __str__(self):
        return self.title

    def serializable_values(self, exclude=[]):
        tree = {}
        for field in self._meta.fields:
            if field.name in exclude:
                continue
            tree[field.name] = self.serializable_value(field.name)
        return tree
