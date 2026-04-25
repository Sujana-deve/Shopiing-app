from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import profile


def login_page(request):
    # Already logged in → go home
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, "Both fields are required.")
            return redirect('login')

        user_obj = User.objects.filter(username=email).first()

        if user_obj is None:
            messages.error(request, "No account found with that email. Please register.")
            return redirect('login')

        # Check email verification
        user_profile = profile.objects.filter(user=user_obj).first()
        if user_profile and not user_profile.is_email_verified:
            messages.warning(request, "Please verify your email before logging in. Check your inbox.")
            return redirect('login')

        user = authenticate(username=email, password=password)

        if user is None:
            messages.error(request, "Incorrect password. Please try again.")
            return redirect('login')

        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name}! 👋")

        # Respect 'next' param (e.g. redirected from cart/checkout)
        next_url = request.GET.get('next')
        return redirect(next_url if next_url else 'index')

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        password   = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # --- Validations ---
        if not all([first_name, last_name, email, password]):
            messages.error(request, "All fields are required.")
            return HttpResponseRedirect(request.path_info)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return HttpResponseRedirect(request.path_info)

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return HttpResponseRedirect(request.path_info)

        if User.objects.filter(username=email).exists():
            messages.warning(request, "An account with this email already exists.")
            return HttpResponseRedirect(request.path_info)

        # --- Create user (profile is auto-created via signal in models.py) ---
        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        messages.success(request, "Account created! Please check your email to verify your account.")
        return redirect('login')

    return render(request, 'accounts/register.html')


def activate_email(request, email_token):
    try:
        user_profile = profile.objects.get(email_token=email_token)
        if user_profile.is_email_verified:
            messages.info(request, "Your email is already verified. Please log in.")
            return redirect('login')

        user_profile.is_email_verified = True
        user_profile.save()
        messages.success(request, "Email verified successfully! You can now log in.")
        return redirect('login')

    except profile.DoesNotExist:
        return HttpResponse(
            "<h2>Invalid or expired activation link.</h2>"
            "<a href='/'>Return Home</a>",
            status=400
        )


@login_required(login_url='login')
def user_profile_page(request):
    user_profile, _ = profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Handle profile image update
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            user_profile.profile_image = profile_image
            user_profile.save()
            messages.success(request, "Profile picture updated!")

        # Handle name update
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        if first_name:
            request.user.first_name = first_name
        if last_name:
            request.user.last_name = last_name
        request.user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('user-profile')

    context = {
        'user_profile': user_profile,
        'orders': [],  # hook up Order model later
    }
    return render(request, 'accounts/profile.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, "You've been logged out. See you soon!")
    return redirect('index')