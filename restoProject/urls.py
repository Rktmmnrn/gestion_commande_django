"""
URL configuration for restoProject project.

"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def index(request):
    return HttpResponse("tape /admin or something else to enter...")

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    path('api/', include('orders.urls')),
]
