from django.urls import path

from . import views

urlpatterns = [
    path("coordinador/", views.coordinador, name="coordinador"),
    path("coordinador/exportar/", views.exportar_reportes, name="coordinador_exportar"),
]
