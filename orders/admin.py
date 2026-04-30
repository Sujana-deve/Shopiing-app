# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model        = OrderItem
    extra        = 0
    readonly_fields = ('product', 'color_variant', 'size_variant', 'quantity', 'price', 'get_total')
    can_delete   = False

    def get_total(self, obj):
        return f"Rs. {obj.get_total()}"
    get_total.short_description = 'Item Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines         = [OrderItemInline]
    list_display    = ('get_short_id', 'user', 'status', 'payment_method', 'payment_status', 'grand_total', 'created_at')
    list_filter     = ('status', 'payment_method', 'payment_status')
    search_fields   = ('user__username', 'user__email', 'phone', 'email')
    readonly_fields = (
        'uid', 'user', 'subtotal', 'shipping_charge', 'grand_total',
        'first_name', 'last_name', 'email', 'phone',
        'address', 'city', 'state', 'zip_code', 'country',
        'created_at', 'updated_at',
    )
    list_editable   = ('status', 'payment_status')
    ordering        = ('-created_at',)

    fieldsets = (
        ('Order Info', {
            'fields': ('uid', 'user', 'status', 'payment_method', 'payment_status')
        }),
        ('Shipping Address', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_charge', 'grand_total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )