import stripe
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Item, Order
from .services import ItemPaymentService

stripe.api_key = settings.STRIPE_SECRET_KEY


class IndexView(TemplateView):
    template_name = "payments/index.html"


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
        domain = ""
        if settings.DEBUG:
            domain = settings.DOMAIN_URL
        try:
            checkout_session = ItemPaymentService.get_session(
                pk,
                success_url=domain + reverse("payments:buy_success"),
                cancel_url=domain
                + reverse("payments:item-detail", kwargs={"pk": pk}),
            )
            return JsonResponse({"session_id": checkout_session.id})
        except Exception as e:
            JsonResponse(data=str(e), status=403)


class ItemList(ListView):
    model = Item
    template_name = "payments/item_list.html"


class OrderList(ListView):
    model = Order
    template_name = "payments/order_list.html"


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
        try:
            intent = stripe.PaymentIntent.create(
                amount=self.object.get_final_price(),
                currency=self.object.get_currency(),
                payment_method_types=["card"],
                metadata={"integration_check": "accept_a_payment"},
            )
        except Exception as e:
            JsonResponse(data=str(e), status=403)

        context["stripe_pk"] = settings.STRIPE_PUBLIC_KEY
        context["clientSecret"] = intent.client_secret
        return context


class SuccessView(TemplateView):
    template_name = "payments/success.html"
