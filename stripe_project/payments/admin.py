from django import forms
from django.contrib import admin

from .models import Discount, Item, Order, Tax

admin.site.empty_value_display = "-"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "price", "currency")
    list_display_links = ("name",)
    readonly_fields = ("id",)
    search_fields = ("name",)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["items", "discount", "tax"]

    def clean_items(self):
        values = self.cleaned_data["items"]
        currencies = set([item.currency for item in values])
        if len(currencies) > 1:
            raise forms.ValidationError(
                "Items in the order have different currencies."
            )
        return values


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pk", "discount", "tax")
    form = OrderForm


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percent_off")
    list_display_links = ("name",)
    readonly_fields = ("id",)
    search_fields = ("name",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percent")
    list_display_links = ("name",)
    readonly_fields = ("id",)
    search_fields = ("name",)


admin.site.site_header = "Административная панель Stripe Payments"
admin.site.index_title = "Настройки Stripe Payments"
admin.site.site_title = "Административная панель Stripe Payments"
