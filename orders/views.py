# orders/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart, CartItem
from .models import Order, OrderItem


@login_required
def checkout_page(request):
    try:
        cart  = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Same shipping logic as cart_page view
    subtotal = cart.get_cart_total()
    shipping = 0 if subtotal >= 2000 else 150
    grand_total = subtotal + shipping

    # Pre-fill form with user's existing info
    user = request.user
    initial = {
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'email':      user.email,
    }

    context = {
        'cart':        cart,
        'items':       items,
        'subtotal':    subtotal,
        'shipping':    shipping,
        'grand_total': grand_total,
        'initial':     initial,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')

    try:
        cart  = Cart.objects.get(user=request.user)
        items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if not items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    # Collect form fields
    first_name     = request.POST.get('first_name', '').strip()
    last_name      = request.POST.get('last_name', '').strip()
    email          = request.POST.get('email', '').strip()
    phone          = request.POST.get('phone', '').strip()
    address        = request.POST.get('address', '').strip()
    city           = request.POST.get('city', '').strip()
    state          = request.POST.get('state', '').strip()
    zip_code       = request.POST.get('zip_code', '').strip()
    country        = request.POST.get('country', 'Nepal').strip()
    payment_method = request.POST.get('payment_method', 'cash_on_delivery')

    # Basic validation
    required = [first_name, last_name, email, phone, address, city, state, zip_code]
    if not all(required):
        messages.error(request, "Please fill in all required fields.")
        return redirect('checkout')

    # Calculate totals
    subtotal    = cart.get_cart_total()
    shipping    = 0 if subtotal >= 2000 else 150
    grand_total = subtotal + shipping

    # Create Order
    order = Order.objects.create(
        user           = request.user,
        first_name     = first_name,
        last_name      = last_name,
        email          = email,
        phone          = phone,
        address        = address,
        city           = city,
        state          = state,
        zip_code       = zip_code,
        country        = country,
        payment_method = payment_method,
        subtotal       = subtotal,
        shipping_charge= shipping,
        grand_total    = grand_total,
    )

    # Create OrderItems from CartItems
    for item in items:
        base_price    = item.product.get_discounted_price()
        color_price   = item.color_variant.price if item.color_variant else 0
        size_price    = item.size_variant.price  if item.size_variant  else 0
        item_price    = base_price + color_price + size_price

        OrderItem.objects.create(
            order         = order,
            product       = item.product,
            color_variant = item.color_variant,
            size_variant  = item.size_variant,
            quantity      = item.quantity,
            price         = item_price,
        )

    # Clear the cart
    items.delete()

    messages.success(request, f"Order placed successfully!")
    return redirect('order-success', order_uid=order.uid)


@login_required
def order_success(request, order_uid):
    order = get_object_or_404(Order, uid=order_uid, user=request.user)
    items = order.items.all()
    return render(request, 'orders/order_success.html', {'order': order, 'items': items})