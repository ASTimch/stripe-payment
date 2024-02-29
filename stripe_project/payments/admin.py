from django.contrib import admin

from .models import Item

admin.site.empty_value_display = "-"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "price")
    list_display_links = ("name",)
    readonly_fields = ("id",)
    search_fields = ("name",)
