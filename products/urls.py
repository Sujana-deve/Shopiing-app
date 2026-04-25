from django.urls import path
from .views import get_product, category_products, all_products

urlpatterns = [
    path('',                        all_products,      name='all-products'),
    path('category/<slug:slug>/',   category_products, name='category-products'),
    path('<slug:slug>/',            get_product,       name='get-product'),
]