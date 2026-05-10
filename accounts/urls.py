from django.urls import path
from .views import login_page, register_page, activate_email, user_profile_page, logout_view

urlpatterns = [
    path('login/',                      login_page,        name='login'),
    path('register/',                   register_page,     name='register'),
    path('logout/',                     logout_view,       name='logout'),
    path('profile/',                    user_profile_page, name='user-profile'),
    path('activate/<str:email_token>/', activate_email,    name='activate'),
]