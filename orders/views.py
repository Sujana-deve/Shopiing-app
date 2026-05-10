import hmac
import hashlib
import base64
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from cart.models import Cart
from .models import Order, OrderItem


# ── eSewa helpers ─────────────────────────────────────────────────────────────

def generate_esewa_signature(total_amount, transaction_uuid, product_code):
    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    h = hmac.new(
        settings.ESEWA_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    return base64.b64encode(h.digest()).decode('utf-8')


def verify_esewa_signature(decoded_data):
    signed_fields = decoded_data.get('signed_field_names', '').split(',')
    message = ','.join([f"{f}={decoded_data.get(f, '')}" for f in signed_fields])
    h = hmac.new(
        settings.ESEWA_SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    )
    expected = base64.b64encode(h.digest()).decode('utf-8')
    return expected == decoded_data.get('signature', '')


# ── Checkout ──────────────────────────────────────────────────────────────────

@login_required
def checkout_page(request):
    try:
        cart  = Cart.objects.get(user=request.user)
        items = cart.cart_items.select_related('product', 'color_variant', 'size_variant').all()
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    subtotal    = cart.get_cart_total()
    shipping    = 0 if subtotal >= 2000 else 150
    grand_total = subtotal + shipping

    initial = {
        'first_name': request.user.first_name,
        'last_name':  request.user.last_name,
        'email':      request.user.email,
    }

    return render(request, 'orders/checkout.html', {
        'items':       items,
        'subtotal':    subtotal,
        'shipping':    shipping,
        'grand_total': grand_total,
        'initial':     initial,
    })


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    try:
        cart  = Cart.objects.get(user=request.user)
        items = cart.cart_items.select_related('product', 'color_variant', 'size_variant').all()
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    subtotal    = cart.get_cart_total()
    shipping    = 0 if subtotal >= 2000 else 150
    grand_total = subtotal + shipping

    order = Order.objects.create(
        user            = request.user,
        first_name      = request.POST.get('first_name', '').strip(),
        last_name       = request.POST.get('last_name', '').strip(),
        email           = request.POST.get('email', '').strip(),
        phone           = request.POST.get('phone', '').strip(),
        address         = request.POST.get('address', '').strip(),
        city            = request.POST.get('city', '').strip(),
        state           = request.POST.get('state', '').strip(),
        zip_code        = request.POST.get('zip_code', '').strip(),
        country         = request.POST.get('country', 'Nepal').strip(),
        subtotal        = subtotal,
        shipping_charge = shipping,
        grand_total     = grand_total,
        payment_method  = request.POST.get('payment_method', 'cash_on_delivery'),
    )

    for item in items:
        price = item.product.get_discounted_price()
        if item.color_variant:
            price += item.color_variant.price
        if item.size_variant:
            price += item.size_variant.price

        OrderItem.objects.create(
            order         = order,
            product       = item.product,
            color_variant = item.color_variant,
            size_variant  = item.size_variant,
            quantity      = item.quantity,
            price         = price,
        )

    items.delete()

    if order.payment_method == 'esewa':
        return redirect('initiate-esewa-payment', order_uid=order.uid)

    messages.success(request, f"Order #{order.get_short_id()} placed successfully!")
    return redirect('order-success', order_uid=order.uid)


# ── eSewa views ───────────────────────────────────────────────────────────────

@login_required
def initiate_esewa_payment(request, order_uid):
    order = get_object_or_404(Order, uid=order_uid, user=request.user)

    total_amount     = f"{order.grand_total:.2f}"
    transaction_uuid = str(order.uid)          # full UUID — unique, easy to look up on return
    product_code     = settings.ESEWA_MERCHANT_CODE
    signature        = generate_esewa_signature(total_amount, transaction_uuid, product_code)

    return render(request, 'orders/esewa_redirect.html', {
        'order':            order,
        'esewa_url':        settings.ESEWA_PAYMENT_URL,
        'total_amount':     total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code':     product_code,
        'signature':        signature,
        'success_url':      request.build_absolute_uri(reverse('esewa-success')),
        'failure_url':      request.build_absolute_uri(reverse('esewa-failure')),
    })


@login_required
def esewa_success(request):
    encoded_data = request.GET.get('data')
    if not encoded_data:
        messages.error(request, "Invalid payment response.")
        return redirect('order-history')

    try:
        decoded_data = json.loads(base64.b64decode(encoded_data).decode('utf-8'))
    except Exception:
        messages.error(request, "Could not read payment response.")
        return redirect('order-history')

    if not verify_esewa_signature(decoded_data):
        messages.error(request, "Payment verification failed — possible tampering.")
        return redirect('order-history')

    transaction_uuid = decoded_data.get('transaction_uuid')  # str(order.uid)

    try:
        order = Order.objects.get(uid=transaction_uuid, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('order-history')

    if decoded_data.get('status') == 'COMPLETE':
        order.payment_status = 'paid'
        order.status         = 'processing'
        order.save()
        messages.success(request, f"Payment successful! Order #{order.get_short_id()} confirmed.")
        return redirect('order-success', order_uid=order.uid)

    messages.error(request, "Payment incomplete.")
    return redirect('order-history')


@login_required
def esewa_failure(request):
    messages.error(request, "Payment failed or was cancelled. Your order is saved — you can retry from order history.")
    return redirect('order-history')


# ── Order success / history ───────────────────────────────────────────────────

@login_required
def order_success(request, order_uid):
    order = get_object_or_404(Order, uid=order_uid, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders/order_history.html', {'orders': orders})