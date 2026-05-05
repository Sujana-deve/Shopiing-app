import uuid
from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel


class Category(BaseModel):
    category_name  = models.CharField(max_length=100)
    slug           = models.SlugField(unique=True)
    category_image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.category_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price      = models.IntegerField(default=0)

    def __str__(self):
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price     = models.IntegerField(default=0)

    def __str__(self):
        return self.size_name


class Product(BaseModel):
    product_name = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True)
    category     = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='products')
    description  = models.TextField(blank=True)
    price        = models.IntegerField()
    discount     = models.IntegerField(default=0)
    stock        = models.IntegerField(default=0)
    is_featured  = models.BooleanField(default=False)
    product_images = models.ImageField(upload_to='products/', blank=True, null=True)
    color_variant  = models.ManyToManyField(ColorVariant, blank=True)
    size_variant   = models.ManyToManyField(SizeVariant, blank=True)

    def __str__(self):
        return self.product_name

    def get_discounted_price(self):
        if self.discount:
            return self.price - (self.price * self.discount / 100)
        return self.price

    def is_in_stock(self):
        return self.stock > 0

    # ── NEW ──────────────────────────────────────────────
    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    def get_review_count(self):
        return self.reviews.count()
    # ─────────────────────────────────────────────────────


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.product_name}"


# ── NEW MODEL ────────────────────────────────────────────
class Review(BaseModel):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user    = models.ForeignKey(User,    on_delete=models.CASCADE, related_name='reviews')
    rating  = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ('product', 'user')   # one review per user per product

    def __str__(self):
        return f"{self.user.username} → {self.product.product_name} ({self.rating}★)"
# ─────────────────────────────────────────────────────────