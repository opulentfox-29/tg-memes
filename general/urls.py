from django.contrib import admin
from django.urls import path, include

from .views import index, settings

urlpatterns = [
    path('', index, name='home'),
    path('settings/', settings, name='settings'),
]
