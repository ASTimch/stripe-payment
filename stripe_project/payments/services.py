import stripe
from django.shortcuts import get_object_or_404
from stripe.checkout import Session

from .models import Item, Order, ShippingTax


class DiscountService:
    @classmethod
    def create_coupon(cls, coupon_id: str, name: str, percent_off: int):
        stripe.Coupon.create(
            name=name,
            duration="forever",
            id=coupon_id,
            percent_off=percent_off,
        )

    @classmethod
    def generate_coupon_id(cls, id: int) -> str:
        return "coupon_" + str(id)

    @classmethod
    def update_coupon(cls, coupon_id: str, name: str, percent_off: int):
        try:
            stripe.Coupon.delete(coupon_id)
        except Exception:
            pass  # coupon is not exist
        stripe.Coupon.create(
            name=name,
            duration="forever",
            id=coupon_id,
            percent_off=percent_off,
        )


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
            metadata={"product_id": item.id},
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return checkout_session


class ShippingTaxService:
    @classmethod
    def get_shipping_rate_data(cls, tax: ShippingTax):
        """Возвращает словарь для заданного объекта tax."""

        return {
            "display_name": tax.name,
            "fixed_amount": {
                "amount": tax.amount,
                "currency": tax.currency,
            },
            "tax_behavior": tax.behavior,
            "tax_code": tax.code,  # "txcd_92010001"
            "type": "fixed_amount",
        }


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
    def get_discounts_data(cls, order: Order) -> list[dict]:
        if not order.discount:
            return []
        coupon_id = DiscountService.generate_coupon_id(order.discount.id)
        return [{"coupon": coupon_id}]

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
            Order.objects.select_related("tax", "discount").prefetch_related(
                "items"
            ),
            pk=pk,
        )
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=cls.get_price_data(order),
            discounts=cls.get_discounts_data(order),
            metadata={"order_id": order.id},
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            shipping_options=[
                {
                    "shipping_rate_data": ShippingTaxService.get_shipping_rate_data(
                        order.tax
                    )
                }
            ],
        )
        return checkout_session
