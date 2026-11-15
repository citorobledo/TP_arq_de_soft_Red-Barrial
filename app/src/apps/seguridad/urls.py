from django.urls import path
from .deposito import deposito
from .coordinador import coordinador, exportar_reportes

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.panel, name="panel"),
    path("deposito/", deposito, name="deposito"),
    path("coordinador/", coordinador, name="coordinador"),
    path("coordinador/exportar/", exportar_reportes, name="coordinador_exportar"),

]
