from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def get_product(request, slug):
    product    = get_object_or_404(Product, slug=slug)
    images     = product.product_images.all()
    related    = Product.objects.filter(
                    category=product.category
                 ).exclude(uid=product.uid)[:4]

    # Collect selected variants from URL params (e.g. ?color=Red&size=M)
    selected_color = request.GET.get('color', None)
    selected_size  = request.GET.get('size', None)

    context = {
        'product':        product,
        'images':         images,
        'related':        related,
        'selected_color': selected_color,
        'selected_size':  selected_size,
        'colors':         product.color_variant.all(),
        'sizes':          product.size_variant.all(),
    }
    return render(request, 'products/product.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.all()

    # Optional price filter from query params (?min=100&max=500)
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category.html', context)


def all_products(request):
    products   = Product.objects.all()
    categories = Category.objects.all()

    # Filter by category slug
    cat_slug = request.GET.get('category')
    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    # Search by name
    query = request.GET.get('q')
    if query:
        products = products.filter(product_name__icontains=query)

    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    context = {
        'products':   products,
        'categories': categories,
        'query':      query,
        'sort':       sort,
    }
    return render(request, 'products/all_products.html', context)