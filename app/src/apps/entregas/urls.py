from django.urls import path

from . import views

urlpatterns = [
    path("entregas/", views.entregas, name="entregas"),
    path("entregas/nueva/", views.nueva_entrega, name="nueva_entrega"),
]
