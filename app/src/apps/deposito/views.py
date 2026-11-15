"""Panel del voluntario de depósito."""

from django.shortcuts import render

from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import VOLUNTARIO_DEPOSITO


@rol_requerido(VOLUNTARIO_DEPOSITO)
def deposito(request):
    # Por ahora no hay modelos conectados a la vista: la plantilla muestra
    # ceros y los mensajes de "todavía no hay...". Se conectan a services.py luego.
    contexto = {
        "resumen": {"stock_kg": 0, "ingresos_hoy": 0, "entregas_hoy": 0, "por_vencer": 0},
        "movimientos": [],
        "lotes_por_vencer": [],
        "comedores": [],
        "lotes": [],
    }
    return render(request, "deposito/deposito.html", contexto)
