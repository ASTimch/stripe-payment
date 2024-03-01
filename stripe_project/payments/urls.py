from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("success/", views.SuccessView.as_view(), name="buy_success"),
    path("item/<int:pk>/", views.ItemDetail.as_view(), name="item-detail"),
    path("buy/<int:pk>/", views.ItemCheckout.as_view(), name="item-checkout"),
    path("order/<int:pk>/", views.OrderDetail.as_view(), name="order-detail"),
    path(
        "order-buy/<int:pk>/",
        views.OrderCheckout.as_view(),
        name="order-checkout",
    ),
]
