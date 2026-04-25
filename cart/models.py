from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from products.models import Product, ColorVariant, SizeVariant


class Cart(BaseModel):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    is_paid    = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart of {self.user.email}"

    # Total item count
    def get_cart_count(self):
        return self.cart_items.count()

    # Raw total before any discount
    def get_cart_total(self):
        return sum(item.get_total_price() for item in self.cart_items.all())


class CartItem(BaseModel):
    cart          = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product       = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity      = models.PositiveIntegerField(default=1)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL,
                                      null=True, blank=True)
    size_variant  = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL,
                                      null=True, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name}"

    def get_total_price(self):
        base  = self.product.get_discounted_price()
        color_price = self.color_variant.price if self.color_variant else 0
        size_price  = self.size_variant.price  if self.size_variant  else 0
        return (base + color_price + size_price) * self.quantity