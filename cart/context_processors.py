from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_paid=False).first()
        count = cart.get_cart_count() if cart else 0
    else:
        count = 0
    return {'cart_count': count}