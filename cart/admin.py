from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model  = CartItem
    extra  = 0
    fields = ['product', 'quantity', 'color_variant', 'size_variant']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ['user', 'get_cart_count', 'get_cart_total', 'is_paid']
    list_filter   = ['is_paid']
    search_fields = ['user__email']
    inlines       = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'color_variant', 'size_variant']