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

    def get_display_price(self) -> str:
        """Цена товара (рублей)."""
        return "{0:.2f}".format(self.price / 100)


class Order(models.Model):
    items = models.ManyToManyField(Item, verbose_name="Список заказов")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        default_related_name = "orders"

    def __str__(self):
        return f"id: {self.pk}"

    def get_absolute_url(self):
        return reverse("payments:order_detail", kwargs={"pk": self.pk})

    def get_order_price(self) -> int:
        """Общая сумма заказа (копеек)."""
        return sum(item.price for item in self.items.all())

    def get_display_price(self) -> str:
        """Общая сумма заказа (рублей)."""
        return "{0:.2f}".format(self.get_order_price() / 100)
