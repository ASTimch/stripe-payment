from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Currency(models.TextChoices):
    USD = "usd", "$USD"
    RUB = "rub", "Рубль"


class TaxBehavior(models.TextChoices):
    INCLUSIVE = "inclusive"
    EXCLUSIVE = "exclusive"


class CurrencyMixin(models.Model):
    currency = models.CharField(
        max_length=5,
        verbose_name="Валюта",
        choices=Currency.choices,
        default=Currency.RUB,
    )


class Item(CurrencyMixin):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    description = models.CharField(max_length=255, verbose_name="Описание")
    price = models.PositiveIntegerField(verbose_name="Цена (коп)")

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
    percent_off = models.DecimalField(
        max_digits=6,
        decimal_places=2,
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
    description = models.CharField(max_length=255, verbose_name="Описание")
    percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Величина налога в %",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    behavior = models.CharField(
        max_length=15,
        verbose_name="Тип",
        choices=TaxBehavior.choices,
        default=TaxBehavior.EXCLUSIVE,
    )
    tax_id = models.CharField(
        max_length=50,
        verbose_name="Идентификатор stripe",
    )

    class Meta:
        verbose_name = "Налог"
        verbose_name_plural = "Налоги"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} {self.percentage}% ({self.behavior})"


class ShippingTax(CurrencyMixin):
    name = models.CharField(max_length=255, verbose_name="Наименование")
    amount = models.PositiveIntegerField(
        verbose_name="Стоимость доставки (коп)"
    )
    behavior = models.CharField(
        max_length=15,
        verbose_name="Тип",
        choices=TaxBehavior.choices,
        default=TaxBehavior.EXCLUSIVE,
    )
    code = models.CharField(max_length=15, verbose_name="Налоговый код")

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставка"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} {self.amount / 100} ({self.currency})"


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
    shipping = models.ForeignKey(
        ShippingTax,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Доставка",
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

    def get_tax_amount_inclusive(self) -> int:
        """Cумма налога включенного в стоимость (копеек)."""
        if self.tax and self.tax.behavior == TaxBehavior.INCLUSIVE:
            return (
                self.get_order_subtotal()
                * self.tax.percentage
                // (100 + self.tax.percentage)
            )
        return 0

    def get_tax_amount(self) -> int:
        """Cумма налога вне зависимости от типа (копеек)."""
        return self.get_tax_amount_exlusive() + self.get_tax_amount_inclusive()

    def get_tax_amount_exlusive(self) -> int:
        """Cумма дополнительно налога (копеек)."""
        if self.tax and self.tax.behavior == TaxBehavior.EXCLUSIVE:
            return self.get_order_subtotal() * self.tax.percentage // 100
        return 0

    def get_shipping_amount(self) -> int:
        """Cумма доставки (копеек)."""
        if self.shipping:
            return self.shipping.amount
        return 0

    def get_final_price(self) -> int:
        """Итоговая сумма заказа (копеек)."""
        return (
            self.get_order_subtotal()
            + self.get_tax_amount_exlusive()
            + self.get_shipping_amount()
        )

    def get_currency(self) -> str:
        """Текущая валюта заказа."""
        if self.items.exists():
            return self.items.first().currency
        return settings.DEFAULT_CURRENCY
