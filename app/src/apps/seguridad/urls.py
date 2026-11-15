from django.urls import path
from .deposito import deposito
from .comedor import comedor, recibir_entrega

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.panel, name="panel"),
    path("deposito/", deposito, name="deposito"),
    path("comedor/", comedor, name="comedor"),
    path("comedor/recibir/<int:pk>/", recibir_entrega, name="recibir_entrega"),

]
