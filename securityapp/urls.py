from django.urls import path
from . import views

urlpatterns = [
    # custom login and registration
    path('',                   views.login_view,       name='login'),
    path('register/',          views.register_view,    name='register'),

    # protected pages
    path('dashboard/',         views.dashboard_view,   name='dashboard'),
    path('change-username/',   views.change_username,  name='change_username'),
    path('security/',          views.security_view,    name='security'),
    path('video_feed/',        views.video_feed,       name='video_feed'),
    path('logout/',            views.logout_view,      name='logout'),
path('password-change/', views.password_change_view, name='password_change'),
]