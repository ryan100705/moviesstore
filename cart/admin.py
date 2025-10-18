from django.contrib import admin
from .models import Order, Item

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total", "city", "state", "region_code", "date")
    list_filter = ("state", "region_code", "date")
    search_fields = ("user__username", "city", "state", "region_code")

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "movie", "price", "quantity")
    search_fields = ("movie__name",)