from django.urls import path

from . import views

urlpatterns = [
    path("comedor/", views.comedor, name="comedor"),
    path("comedor/recibir/<int:pk>/", views.recibir_entrega, name="recibir_entrega"),
]
