from django.urls import path
from .deposito import deposito

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("panel/", views.panel, name="panel"),
     path("deposito/", deposito, name="deposito"),

]
