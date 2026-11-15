"""Panel del voluntario de depósito.

Archivo nuevo: no toca views.py. Usa el decorador rol_requerido de
decorators.py: exige sesión iniciada y pertenecer al grupo voluntario_deposito
(si no, muestra seguridad/sin_permisos.html con 403).
"""
from django.shortcuts import render

from .decorators import rol_requerido
from .roles import VOLUNTARIO_DEPOSITO


@rol_requerido(VOLUNTARIO_DEPOSITO)
def deposito(request):
    # Por ahora no hay modelos de lotes ni movimientos: la plantilla muestra
    # ceros y los mensajes de "todavía no hay...". Cuando existan, se cargan acá.
    contexto = {
        "resumen": {"stock_kg": 0, "ingresos_hoy": 0, "entregas_hoy": 0, "por_vencer": 0},
        "movimientos": [],
        "lotes_por_vencer": [],
        "comedores": [],
        "lotes": [],
    }
    return render(request, "seguridad/deposito.html", contexto)
