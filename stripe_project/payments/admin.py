from django import forms
from django.contrib import admin

from .models import Discount, Item, Order, ShippingTax, Tax
from .services import DiscountService, TaxService

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
        fields = ["items", "discount", "tax", "shipping"]

    def clean_items(self):
        values = self.cleaned_data["items"]
        currencies = set([item.currency for item in values])
        if len(currencies) > 1:
            raise forms.ValidationError(
                "Items in the order have different currencies."
            )
        return values

    def clean(self):
        values = self.cleaned_data["items"]
        shipping = self.cleaned_data["shipping"]
        currencies = set([item.currency for item in values])
        if shipping:
            currencies.add(shipping.currency)
        if len(currencies) > 1:
            raise forms.ValidationError(
                "Items and tax in the order have different currencies."
            )


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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        coupon_id = DiscountService.generate_coupon_id(obj.id)
        DiscountService.update_coupon(coupon_id, obj.name, obj.percent_off)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "percentage",
        "behavior",
        "tax_id",
    )
    list_display_links = ("name",)
    readonly_fields = ("id", "tax_id")
    search_fields = ("name",)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # запрещено менять процентную ставку после создания
            return self.readonly_fields + ("bahavior",)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        try:
            TaxService.update_tax(
                obj.tax_id,
                obj.name,
                obj.description,
                obj.percentage,
                obj.behavior,
            )
        except Exception:
            # create new tax
            tax_rate = TaxService.create_tax(
                obj.name,
                obj.description,
                obj.percentage,
                obj.behavior,
            )
            obj.tax_id = tax_rate.id
        super().save_model(request, obj, form, change)


@admin.register(ShippingTax)
class ShippingTaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "amount", "currency")
    list_display_links = ("name",)
    readonly_fields = ("id",)
    search_fields = ("name",)


admin.site.site_header = "Административная панель Stripe Payments"
admin.site.index_title = "Настройки Stripe Payments"
admin.site.site_title = "Административная панель Stripe Payments"
