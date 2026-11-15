"""Pantalla del referente de comedor: confirma la recepción de entregas.

Vista delgada (ADR-15): solo invoca los servicios. Archivo nuevo, mismo patrón
que deposito.py.
"""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.entregas import services as entregas_services
from apps.entregas.models import Entrega

from .decorators import rol_requerido
from .roles import REFERENTE_COMEDOR


def _nombre(usuario):
    return usuario.get_full_name() or usuario.username


@rol_requerido(REFERENTE_COMEDOR)
def comedor(request):
    comedores = list(request.user.comedores.all())  # TODO: usar el servicio de comedores
    pendientes, recibidas = [], []
    for c in comedores:
        pendientes += entregas_services.listar_entregas(
            comedor_id=c.id, estado=Entrega.Estado.REGISTRADA
        )
        recibidas += entregas_services.listar_entregas(
            comedor_id=c.id, estado=Entrega.Estado.CONFIRMADA
        )
    recibidas.sort(key=lambda e: e.fecha_confirmacion, reverse=True)
    hoy = timezone.localdate()
    contexto = {
        "comedores": comedores,
        "pendientes": pendientes,
        "recibidas": recibidas[:20],
        "recibidas_hoy": sum(
            1 for e in recibidas if timezone.localtime(e.fecha_confirmacion).date() == hoy
        ),
    }
    return render(request, "seguridad/comedor.html", contexto)


@require_POST
@rol_requerido(REFERENTE_COMEDOR)
def recibir_entrega(request, pk):
    try:
        entrega = entregas_services.confirmar_recepcion(
            pk, usuario_id=request.user.id, nombre_referente=_nombre(request.user)
        )
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except Entrega.DoesNotExist:
        messages.error(request, "La entrega no existe.")
    else:
        messages.success(request, f"La entrega #{entrega.id} figura como recibida.")
    return redirect("comedor")