from django.urls import path

from . import views

urlpatterns = [
    path("deposito/", views.deposito, name="deposito"),
]
