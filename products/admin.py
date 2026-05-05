from django.contrib import admin
from .models import Category, ColorVariant, SizeVariant, Product, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display       = ['product_name', 'category', 'price', 'discount', 'stock', 'is_featured']
    list_editable      = ['price', 'discount', 'stock', 'is_featured']
    prepopulated_fields = {'slug': ('product_name',)}
    inlines            = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ['category_name', 'slug']
    prepopulated_fields = {'slug': ('category_name',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display  = ['user', 'product', 'rating', 'created_at']
    list_filter   = ['rating']
    search_fields = ['user__username', 'product__product_name']
    readonly_fields = ['user', 'product', 'created_at']


admin.site.register(ColorVariant)
admin.site.register(SizeVariant)