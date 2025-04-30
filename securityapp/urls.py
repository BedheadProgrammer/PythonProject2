from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('security/', views.security_view, name='security'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_redirect, name='dashboard_redirect'),  # or login if not authenticated
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),     # duplicate name but not a syntax error
    path('change-username/', views.change_username, name='change_username'),
    # use built-in auth for login/logout/password-change:
    path('accounts/', include('django.contrib.auth.urls')),
]