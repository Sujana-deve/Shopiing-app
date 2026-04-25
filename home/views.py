from django.shortcuts import render
from products.models import Product


def index(request):
    all_products  = Product.objects.all()
    featured      = Product.objects.filter(is_featured=True)[:8]   # add field later
    new_arrivals  = Product.objects.order_by('-created_at')[:8]     # newest first

    context = {
        'products':     all_products,
        'featured':     featured,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'home/index.html', context)