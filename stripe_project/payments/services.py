import stripe
from django.shortcuts import get_object_or_404
from stripe import PaymentIntent
from stripe.checkout import Session

from .models import Item, Order, ShippingTax, TaxBehavior


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


class TaxService:
    @classmethod
    def create_tax(
        cls,
        name: str,
        description: str,
        percentage: float,
        behavior: TaxBehavior,
    ):
        return stripe.TaxRate.create(
            display_name=name,
            description=description,
            percentage=percentage,
            inclusive=behavior == TaxBehavior.INCLUSIVE,
        )

    @classmethod
    def update_tax(
        cls,
        tax_id: str,
        name: str,
        description: str,
        percentage: float,
        behavior: TaxBehavior,
    ):
        stripe.TaxRate.modify(
            id=tax_id,
            display_name=name,
            description=description,
        )


class ItemPaymentService:
    @classmethod
    def get_price_data(cls, item: Item, tax_rates: list[str] = None) -> dict:
        """Возвращает словарь с данными товарной позиции.

        Args:
            item: Объект товарной позиции.
        """
        if tax_rates is None:
            tax_rates = []
        return {
            "price_data": {
                "currency": item.currency,
                "unit_amount": item.price,
                "product_data": {
                    "name": item.name,
                },
            },
            "quantity": 1,
            "tax_rates": tax_rates,
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
        return stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[cls.get_price_data(item)],
            metadata={"product_id": item.id},
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )


class ShippingTaxService:
    @classmethod
    def get_shipping_rate_data(cls, shipping: ShippingTax):
        """Возвращает словарь для заданного объекта shipping."""

        return {
            "display_name": shipping.name,
            "fixed_amount": {
                "amount": shipping.amount,
                "currency": shipping.currency,
            },
            "tax_behavior": shipping.behavior,
            "tax_code": shipping.code,  # "txcd_92010001"
            "type": "fixed_amount",
        }


class OrderPaymentService:
    @classmethod
    def get_price_data(
        cls, order: Order, tax_rates: list[str] = None
    ) -> list[dict]:
        """Возвращает список словарей с данными товарных позиций заказа.

        Args:
            order: Объект заказа.
        """
        return [
            ItemPaymentService.get_price_data(item, tax_rates)
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
            Order.objects.select_related(
                "tax", "discount", "shipping"
            ).prefetch_related("items"),
            pk=pk,
        )
        shipping_data = ShippingTaxService.get_shipping_rate_data(
            order.shipping
        )
        tax_rates = [order.tax.tax_id] if order.tax else []
        return stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=cls.get_price_data(order, tax_rates),
            discounts=cls.get_discounts_data(order),
            metadata={"order_id": order.id},
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            shipping_options=[{"shipping_rate_data": shipping_data}],
        )

    @classmethod
    def get_intent(cls, order: Order) -> PaymentIntent:
        """Возвращает объект PaymentIntent для заказа.

        Args:
            order: Объект заказа.
        """
        return stripe.PaymentIntent.create(
            amount=order.get_final_price(),
            currency=order.get_currency(),
            payment_method_types=["card"],
            metadata={"integration_check": "accept_a_payment"},
        )
