import stripe
from django.shortcuts import get_object_or_404
from stripe.checkout import Session

from .models import Item, Order


class ItemPaymentService:
    @classmethod
    def get_price_data(cls, item: Item) -> dict:
        """Возвращает словарь с данными товарной позиции.

        Args:
            item: Объект товарной позиции.
        """
        return {
            "price_data": {
                "currency": item.currency,
                "unit_amount": item.price,
                "product_data": {
                    "name": item.name,
                },
            },
            "quantity": 1,
        }

    @classmethod
    def get_session(
        cls, pk: int, success_url: str, cancel_url: str
    ) -> Session:
        """Возвращает объект созданной сессии для товара.

        Args:
            pk: Идентификатор объекта.
            success_url: Адрес перенаправления при успешном выполнении.
            cancel_url: Адрес перенаправления при отмене.
        """
        item = get_object_or_404(Item, pk=pk)
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[cls.get_price_data(item)],
            # discounts=[
            #     {
            #         "coupon": "free-period",
            #     }
            # ],
            metadata={"product_id": item.id},
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session


class OrderPaymentService:
    @classmethod
    def get_price_data(cls, order: Order) -> list[dict]:
        """Возвращает список словарей с данными товарных позиций заказа.

        Args:
            order: Объект заказа.
        """
        return [
            ItemPaymentService.get_price_data(item)
            for item in order.items.all()
        ]

    @classmethod
    def get_session(
        cls, pk: int, success_url: str, cancel_url: str
    ) -> Session:
        """Возвращает объект созданной сессии для заказа.

        Args:
            pk: Идентификатор объекта заказа.
            success_url: Адрес перенаправления при успешном выполнении.
            cancel_url: Адрес перенаправления при отмене.
        """
        order = get_object_or_404(
            Order.objects.prefetch_related("items"), pk=pk
        )
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=cls.get_price_data(order),
            metadata={"order_id": order.id},
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session
