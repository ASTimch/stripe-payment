from django.urls import reverse, reverse_lazy
import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Item


stripe.api_key = settings.STRIPE_SECRET_KEY


def item_detail(request, pk: int):
    item = get_object_or_404(Item, pk=pk)
    context = {"item": item, "stripe_pk": settings.STRIPE_PUBLIC_KEY}
    return render(request, "payments/item_detail.html", context=context)


def buy_item(request, pk: int):
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
        cancel_url=domain + reverse("payments:detail", kwargs={"pk": pk}),
        # success_url=domain + "/buy_success/",
        # cancel_url=domain + "/cancel/",
    )
    return JsonResponse({"session_id": checkout_session.id})


def buy_success(request):
    return HttpResponse("buy success!")
