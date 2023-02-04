from django.contrib import admin
from django.urls import path, include

from .views import Index, SettingsPage

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('settings/', SettingsPage.as_view(), name='settings'),
]
