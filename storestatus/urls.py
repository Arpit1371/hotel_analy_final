from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="storestatus"),
    path("update" , views.update , name = "update"),
]