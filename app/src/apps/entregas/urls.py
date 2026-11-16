from django.urls import path

from . import views

urlpatterns = [
    path("entregas/", views.entregas, name="entregas"),
]
