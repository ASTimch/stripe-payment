from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("success/", views.buy_success, name="buy_success"),
    path("item/<int:pk>/", views.item_detail, name="detail"),
    path("buy/<int:pk>/", views.buy_item, name="buy_item"),
]
