from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product, ColorVariant, SizeVariant
from .models import Cart, CartItem


@login_required(login_url='login')
def cart_page(request):
    cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
    total             = cart.get_cart_total()
    shipping          = 0 if total >= 50 else 5
    grand_total       = total + shipping
    shipping_remaining = max(0, 50 - total)

    context = {
        'cart':               cart,
        'items':              cart.cart_items.select_related('product', 'color_variant', 'size_variant'),
        'shipping':           shipping,
        'grand_total':        grand_total,
        'shipping_remaining': shipping_remaining,
    }
    return render(request, 'cart/cart.html', context)


@login_required(login_url='login')
def add_to_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)

    if not product.is_in_stock():
        messages.error(request, f"Sorry, '{product.product_name}' is out of stock.")
        return redirect('get-product', slug=product.slug)

    color_name = request.POST.get('color')
    size_name  = request.POST.get('size')

    color_variant = ColorVariant.objects.filter(color_name=color_name).first() if color_name else None
    size_variant  = SizeVariant.objects.filter(size_name=size_name).first()    if size_name  else None

    cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        color_variant=color_variant,
        size_variant=size_variant,
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"'{product.product_name}' added to cart!")
    return redirect('cart')


@login_required(login_url='login')
def remove_from_cart(request, cart_item_slug):
    cart_item    = get_object_or_404(CartItem, product__slug=cart_item_slug, cart__user=request.user)
    product_name = cart_item.product.product_name
    cart_item.delete()
    messages.success(request, f"'{product_name}' removed from cart.")
    return redirect('cart')


@login_required(login_url='login')
def update_cart_quantity(request, cart_item_slug):
    cart_item = get_object_or_404(CartItem, product__slug=cart_item_slug, cart__user=request.user)
    action    = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")

    return redirect('cart')