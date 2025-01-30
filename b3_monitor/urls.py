# b3_monitor/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from assets.views import LandingPageView, ProfileUpdateView, SignUpView, CustomLoginView

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing_page'),
    path('admin/', admin.site.urls),
    path('assets/', include('assets.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', 
         auth_views.LogoutView.as_view(next_page='landing_page'), 
         name='logout'
    ),
    path('accounts/profile/', ProfileUpdateView.as_view(), name='profile'),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
]