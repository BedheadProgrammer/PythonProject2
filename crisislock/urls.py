# crisislock/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('securityapp.urls')),        # your app
    path('accounts/', include('django.contrib.auth.urls')),
]
