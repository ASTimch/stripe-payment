from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Item(models.Model):
    class Currency(models.TextChoices):
        USD = "usd", "$USD"
        RUB = "rub", "Рубль"

    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.CharField(max_length=255, verbose_name="Описание")
    price = models.PositiveIntegerField(verbose_name="Цена")
    currency = models.CharField(
        max_length=5,
        verbose_name="Валюта",
        choices=Currency.choices,
        default=Currency.RUB,
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("payments:item_detail", kwargs={"pk": self.pk})


class Discount(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    percent_off = models.PositiveSmallIntegerField(
        verbose_name="Величина скидки в %",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} {self.percent_off}%"


class Tax(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    percent = models.PositiveSmallIntegerField(
        verbose_name="Величина налога в %",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} {self.percent}%"


class Order(models.Model):
    items = models.ManyToManyField(Item, verbose_name="Список заказов")
    discount = models.ForeignKey(
        Discount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Скидка",
    )
    tax = models.ForeignKey(
        Tax,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Налог",
    )

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

    def get_discount_amount(self) -> int:
        """Cумма скидки (копеек)."""
        if self.discount:
            return self.get_order_price() * self.discount.percent_off // 100
        return 0

    def get_order_subtotal(self) -> int:
        return self.get_order_price() - self.get_discount_amount()

    def get_tax_amount(self) -> int:
        """Cумма налога (копеек)."""
        if self.tax:
            return self.get_order_subtotal() * self.tax.percent // 100
        return 0

    def get_final_price(self) -> int:
        """Cумма налога (копеек)."""
        return self.get_order_subtotal() + self.get_tax_amount()
