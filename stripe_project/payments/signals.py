from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Item, Order


@receiver(m2m_changed, sender=Order.items.through)
def order_same_currency_validator(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    if action == "pre_add":
        exist_currencies = set(
            [item.currency for item in instance.items.all()]
        )
        added_currencies = set(
            [item.currency for item in Item.objects.filter(pk__in=pk_set)]
        )
        if len(exist_currencies | added_currencies) > 1:
            raise ValidationError(
                "Order items should have the same currencies"
            )
