"""Pantalla del referente de comedor: confirma la recepción de entregas."""

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.comedores import services as comedores_services
from apps.entregas import services as entregas_services
from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import REFERENTE_COMEDOR


def _nombre(usuario) -> str:
    return usuario.get_full_name() or usuario.username


@rol_requerido(REFERENTE_COMEDOR)
def comedor(request):
    comedores = comedores_services.listar_comedores(usuario_id=request.user.id)
    pendientes, recibidas = [], []
    for c in comedores:
        pendientes += entregas_services.listar_entregas(
            comedor_id=c.id, estado="registrada"
        )
        recibidas += entregas_services.listar_entregas(
            comedor_id=c.id, estado="confirmada"
        )
    recibidas.sort(key=lambda e: e.fecha_confirmacion, reverse=True)
    hoy = timezone.localdate()
    contexto = {
        "comedores": comedores,
        "pendientes": pendientes,
        "recibidas": recibidas[:20],
        "recibidas_hoy": sum(
            1
            for e in recibidas
            if e.fecha_confirmacion and timezone.localtime(e.fecha_confirmacion).date() == hoy
        ),
    }
    return render(request, "comedores/comedor.html", contexto)


@require_POST
@rol_requerido(REFERENTE_COMEDOR)
def recibir_entrega(request, pk: int):
    try:
        entrega = entregas_services.confirmar_recepcion(
            pk, usuario_id=request.user.id, nombre_referente=_nombre(request.user)
        )
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except ObjectDoesNotExist:
        messages.error(request, "La entrega no existe.")
    else:
        messages.success(request, f"La entrega #{entrega.id} figura como recibida.")
    return redirect("comedor")
