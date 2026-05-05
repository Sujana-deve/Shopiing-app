from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Review


def get_product(request, slug):
    product          = get_object_or_404(Product, slug=slug)
    images           = product.images.all()
    colors           = product.color_variant.all()
    sizes            = product.size_variant.all()
    related          = Product.objects.filter(
                           category=product.category).exclude(slug=slug)[:4]

    reviews          = product.reviews.select_related('user').order_by('-created_at')
    user_review      = reviews.filter(user=request.user).first() \
                       if request.user.is_authenticated else None

    context = {
        'product':        product,
        'images':         images,
        'colors':         colors,
        'sizes':          sizes,
        'related':        related,
        'reviews':        reviews,
        'user_review':    user_review,
        'average_rating': product.get_average_rating(),
        'review_count':   product.get_review_count(),
        'rating_range':   range(1, 6),
    }
    return render(request, 'products/product.html', context)


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(request, 'products/category.html',
                  {'category': category, 'products': products})


def all_products(request):
    products   = Product.objects.all()
    categories = Category.objects.all()

    q             = request.GET.get('q', '')
    sort          = request.GET.get('sort', '')
    category_slug = request.GET.get('category', '')

    if q:
        products = products.filter(product_name__icontains=q)
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    context = {
        'products':          products,
        'categories':        categories,
        'q':                 q,
        'sort':              sort,
        'selected_category': category_slug,
    }
    return render(request, 'products/all_products.html', context)


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        rating  = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating:
            messages.error(request, 'Please select a star rating.')
            return redirect('get-product', slug=slug)

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': int(rating), 'comment': comment}
        )
        messages.success(request, 'Your review has been submitted!')

    return redirect('get-product', slug=slug)