from django.contrib import admin

from .models import Item, Order

admin.site.empty_value_display = "-"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "price")
    list_display_links = ("name",)
    readonly_fields = ("id",)
    search_fields = ("name",)


class ItemInline(admin.TabularInline):
    model = Order.items.through
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (ItemInline,)
    list_display = ("pk",)


admin.site.site_header = "Административная панель Stripe Payments"
admin.site.index_title = "Настройки Stripe Payments"
admin.site.site_title = "Административная панель Stripe Payments"
