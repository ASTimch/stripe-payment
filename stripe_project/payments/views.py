import stripe
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

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
                        "currency": item.currency,
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


class ItemList(ListView):
    model = Item
    template_name = "payments/item_list.html"


class OrderDetail(DetailView):
    model = Order
    template_name = "payments/order_detail.html"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pk"] = settings.STRIPE_PUBLIC_KEY
        return context


class OrderCheckout(DetailView):
    model = Order
    template_name = "payments/order_checkout.html"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        intent = stripe.PaymentIntent.create(
            amount=self.object.get_final_price(),
            currency="usd",
            payment_method_types=["card"],
            metadata={"integration_check": "accept_a_payment"},
        )
        context["stripe_pk"] = settings.STRIPE_PUBLIC_KEY
        context["clientSecret"] = intent.client_secret
        return context


class SuccessView(TemplateView):
    template_name = "payments/success.html"
