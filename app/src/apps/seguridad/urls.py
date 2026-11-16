from django.urls import path
from .deposito import deposito
from .coordinador import coordinador, exportar_reportes
from .comedor import comedor, recibir_entrega

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.panel, name="panel"),
    path("deposito/", deposito, name="deposito"),
    path("coordinador/", coordinador, name="coordinador"),
    path("coordinador/exportar/", exportar_reportes, name="coordinador_exportar"),  # respetá el name real que tenga
    path("comedor/", comedor, name="comedor"),
    path("comedor/recibir/<int:pk>/", recibir_entrega, name="recibir_entrega"),  # idem
]