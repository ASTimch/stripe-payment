import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from django.views.generic.detail import DetailView

from .models import Item, Order

stripe.api_key = settings.STRIPE_SECRET_KEY


class ItemDetail(DetailView):
    model = Item
    template_name = "payments/item_detail.html"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pk"] = settings.STRIPE_PUBLIC_KEY
        return context


class ItemCheckout(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        item = get_object_or_404(Item, pk=pk)
        domain = ""
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": item.price,
                        "product_data": {
                            "name": item.name,
                        },
                    },
                    "quantity": 1,
                },
            ],
            metadata={"product_id": item.id},
            mode="payment",
            success_url=domain + reverse("payments:buy_success"),
            cancel_url=domain
            + reverse("payments:item-detail", kwargs={"pk": pk}),
        )
        return JsonResponse({"session_id": checkout_session.id})


class OrderDetail(DetailView):
    model = Order
    template_name = "payments/order_detail.html"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pk"] = settings.STRIPE_PUBLIC_KEY
        return context


class OrderCheckout(View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        order = get_object_or_404(
            Order.objects.prefetch_related("items"), pk=pk
        )
        domain = ""
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": order.get_order_price(),
                        "product_data": {
                            "name": str(order),
                        },
                    },
                    "quantity": 1,
                },
            ],
            metadata={"product_id": order.id},
            mode="payment",
            success_url=domain + reverse("payments:buy_success"),
            cancel_url=domain
            + reverse("payments:order-detail", kwargs={"pk": pk}),
        )
        return JsonResponse({"session_id": checkout_session.id})


def buy_success(request):
    return HttpResponse("buy success!")
