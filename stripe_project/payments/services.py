import stripe
from django.shortcuts import get_object_or_404
from stripe.checkout import Session

from .models import Item


class ItemPaymentService:
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
            line_items=[
                {
                    "price_data": {
                        "currency": item.currency,
                        "unit_amount": item.price,
                        "product_data": {
                            "name": item.name,
                        },
                    },
                    "quantity": 1,
                },
            ],
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
