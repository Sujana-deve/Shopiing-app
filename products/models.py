from django.db import models
from base.models import BaseModel
from django.utils.text import slugify


class Category(BaseModel):
    category_name  = models.CharField(max_length=100)
    slug           = models.SlugField(unique=True, blank=True)
    category_image = models.ImageField(upload_to="categories")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price      = models.IntegerField(default=0)   # extra charge for this color

    def __str__(self):
        return self.color_name


class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100)
    price     = models.IntegerField(default=0)    # extra charge for this size

    def __str__(self):
        return self.size_name


class Product(BaseModel):
    product_name   = models.CharField(max_length=100)
    slug           = models.SlugField(unique=True, blank=True)
    category       = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description    = models.TextField(blank=True, null=True)
    price          = models.IntegerField()
    color_variant  = models.ManyToManyField(ColorVariant, blank=True)
    size_variant   = models.ManyToManyField(SizeVariant, blank=True)
    is_featured    = models.BooleanField(default=False)
    stock          = models.PositiveIntegerField(default=10)
    discount       = models.IntegerField(default=0, help_text="Discount % e.g. 10 for 10%")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.product_name)
        super().save(*args, **kwargs)

    # Final price after discount
    def get_discounted_price(self):
        if self.discount > 0:
            return int(self.price - (self.price * self.discount / 100))
        return self.price

    # Is product in stock?
    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.product_name


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image   = models.ImageField(upload_to="products")

    def __str__(self):
        return f"Image for {self.product.product_name}"