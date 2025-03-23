from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('security/', views.security_view, name='security'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('logout/', views.logout_view, name='logout'),
]
