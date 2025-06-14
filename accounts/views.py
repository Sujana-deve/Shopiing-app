from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect,HttpResponse
from .models import profile

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=email).first()

        if user_obj is None:
            messages.error(request, "User does not exist. Please register.")
            return redirect('login')  # Replace 'login' with your actual URL name

        user = authenticate(username=email, password=password)

        if user is None:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect('login')

        login(request, user)
        messages.success(request, "You have successfully logged in.")
        return redirect('/')  # Redirect to homepage or dashboard

    return render(request, 'accounts/login.html')


def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(request.POST)

        if User.objects.filter(username=email).exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        user_obj = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')  # Replace 'login' with your login URL name

    return render(request, 'accounts/register.html')

def activate_email(request,email_token):
    try:
        user = profile.objects.get(email_token = email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse("invalid email token")

