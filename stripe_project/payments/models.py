from django.db import models
from django.urls import reverse


class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.CharField(max_length=255, verbose_name="Описание")
    price = models.PositiveIntegerField(verbose_name="Цена")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("payments:item_detail", kwargs={"pk": self.pk})

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
