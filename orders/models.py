# orders/models.py

from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from products.models import Product, ColorVariant, SizeVariant


class Order(BaseModel):

    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('processing', 'Processing'),
        ('shipped',    'Shipped'),
        ('delivered',  'Delivered'),
        ('cancelled',  'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('online',           'Online Payment'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid',   'Paid'),
    ]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash_on_delivery')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    # Shipping address snapshot
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField()
    phone       = models.CharField(max_length=20)
    address     = models.TextField()
    city        = models.CharField(max_length=100)
    state       = models.CharField(max_length=100)
    zip_code    = models.CharField(max_length=20)
    country     = models.CharField(max_length=100, default='Nepal')

    # Pricing snapshot
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total     = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{str(self.uid)[:8].upper()} — {self.user.username}"

    def get_short_id(self):
        return str(self.uid)[:8].upper()


class OrderItem(BaseModel):

    order         = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product       = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant  = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity      = models.PositiveIntegerField(default=1)
    price         = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot at order time

    def __str__(self):
        return f"{self.product.product_name} x{self.quantity}"

    def get_total(self):
        return self.price * self.quantity
    
PAYMENT_METHOD_CHOICES = [
    ('cash_on_delivery', 'Cash on Delivery'),
    ('online',           'Online Payment'),
    ('esewa',            'eSewa'),
]