from django.urls import path
from .views import (
    checkout_page, place_order,
    order_success, order_history,
    initiate_esewa_payment, esewa_success, esewa_failure,
)

urlpatterns = [
    path('checkout/',                      checkout_page,            name='checkout'),
    path('place-order/',                   place_order,              name='place-order'),
    path('success/<uuid:order_uid>/',      order_success,            name='order-success'),
    path('history/',                       order_history,            name='order-history'),
    path('esewa/pay/<uuid:order_uid>/',    initiate_esewa_payment,   name='initiate-esewa-payment'),
    path('esewa/success/',                 esewa_success,            name='esewa-success'),
    path('esewa/failure/',                 esewa_failure,            name='esewa-failure'),
]