from django.contrib import admin
from .models import Category, Product, ProductImage, ColorVariant, SizeVariant


class ProductImageInline(admin.TabularInline):
    model  = ProductImage
    extra  = 3   # shows 3 empty image slots by default


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display    = ['product_name', 'category', 'price', 'discount',
                       'stock', 'is_featured']
    list_editable   = ['price', 'discount', 'stock', 'is_featured']
    list_filter     = ['category', 'is_featured']
    search_fields   = ['product_name']
    prepopulated_fields = {'slug': ('product_name',)}
    inlines         = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ['category_name', 'slug']
    prepopulated_fields = {'slug': ('category_name',)}


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display  = ['color_name', 'price']
    list_editable = ['price']


@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display  = ['size_name', 'price']
    list_editable = ['price']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']