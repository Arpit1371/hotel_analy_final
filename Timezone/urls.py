from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="timezone"),
    path("update", views.update, name="timezone"),
]