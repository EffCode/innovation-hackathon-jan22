from django.urls import path

from .api import GupShupWebHook

urlpatterns = [
    path("", GupShupWebHook.as_view())
]
