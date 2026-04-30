# orders/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('checkout/',        views.checkout_page, name='checkout'),
    path('place-order/',     views.place_order,   name='place-order'),
    path('success/<uuid:order_uid>/', views.order_success, name='order-success'),
]