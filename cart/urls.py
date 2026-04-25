from django.urls import path
from .views import cart_page, add_to_cart, remove_from_cart, update_cart_quantity

urlpatterns = [
    path('',                               cart_page,            name='cart'),
    path('add/<slug:product_slug>/',       add_to_cart,          name='add-to-cart'),
    path('remove/<slug:cart_item_slug>/',  remove_from_cart,     name='remove-from-cart'),
    path('update/<slug:cart_item_slug>/',  update_cart_quantity, name='update-cart'),
]