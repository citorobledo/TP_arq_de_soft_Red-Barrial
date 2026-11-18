"""Vistas HTML del módulo Entregas (historial inmutable con anulación y alta de entregas)."""

from datetime import date, timedelta

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import redirect, render

from apps.comedores import services as comedor_services
from apps.deposito import services as deposito_services
from apps.entregas import services as entrega_services
from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import VOLUNTARIO_DEPOSITO

from .models import Entrega


def _resumen_deposito(hoy: date) -> dict:
    limite_vencimiento = hoy + timedelta(days=7)
    todos_los_lotes = deposito_services.listar_lotes()
    lista_entregas = entrega_services.listar_entregas()
    return {
        "stock_kg": sum(l.stock for l in todos_los_lotes),
        "ingresos_hoy": len(todos_los_lotes),
        "entregas_hoy": sum(1 for e in lista_entregas if e.fecha == hoy),
        "por_vencer": sum(
            1
            for l in todos_los_lotes
            if l.stock > 0 and hoy <= l.fecha_vencimiento <= limite_vencimiento
        ),
    }


@rol_requerido(VOLUNTARIO_DEPOSITO)
def entregas(request):
    error = None

    if request.method == "POST":
        accion = request.POST.get("accion", "")
        if accion == "anular_entrega":
            try:
                entrega_id = int(request.POST.get("entrega_id", "0"))
                entrega_services.actualizar_entrega(
                    entrega_id, estado=Entrega.Estado.ANULADA
                )
                messages.success(request, f"Entrega #{entrega_id} anulada correctamente.")
                return redirect("entregas")
            except ObjectDoesNotExist:
                error = "La entrega seleccionada no existe."
            except ValidationError as exc:
                error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
            except ValueError:
                error = "Identificador de entrega inválido."

    hoy = date.today()
    todos_los_lotes = deposito_services.listar_lotes()
    comedores = comedor_services.listar_comedores()
    lista_entregas = entrega_services.listar_entregas()

    mapa_comedores = {c.id: f"{c.codigo} - {c.nombre}" for c in comedores}
    mapa_lotes = {
        l.id: f"{l.numero_lote} ({l.nombre_producto})" for l in todos_los_lotes
    }

    entregas_vista = [
        {
            "id": e.id,
            "fecha": e.fecha,
            "comedor": mapa_comedores.get(e.comedor_id, f"ID #{e.comedor_id}"),
            "estado": e.estado,
            "nombre_voluntario": e.nombre_voluntario,
            "detalles": [
                {
                    "lote": mapa_lotes.get(d.lote_id, f"Lote #{d.lote_id}"),
                    "cantidad": d.cantidad,
                }
                for d in e.detalles
            ],
        }
        for e in lista_entregas
    ]

    contexto = {
        "resumen": _resumen_deposito(hoy),
        "entregas": entregas_vista,
        "error": error,
    }
    return render(request, "entregas/entregas.html", contexto)


@rol_requerido(VOLUNTARIO_DEPOSITO)
def nueva_entrega(request):
    error = None

    if request.method == "POST":
        try:
            comedor_id = int(request.POST.get("comedor", "0"))
            comedor = comedor_services.obtener_comedor(comedor_id)
            if not comedor.habilitado:
                raise ValidationError(
                    "No se pueden registrar entregas para un comedor no habilitado."
                )
            lote_ids = request.POST.getlist("lote_id")
            cantidades = request.POST.getlist("cantidad")
            detalles = [
                {"lote_id": int(lid), "cantidad": int(float(qty))}
                for lid, qty in zip(lote_ids, cantidades)
                if lid and qty
            ]
            if not detalles:
                raise ValidationError("Debés agregar al menos un lote con su cantidad.")

            fecha_str = request.POST.get("fecha", "").strip()
            fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
            voluntario = request.user.get_full_name() or request.user.username
            entrega_services.crear_entrega(
                fecha=fecha,
                nombre_voluntario=voluntario,
                comedor_id=comedor_id,
                detalles=detalles,
            )
            messages.success(request, "Entrega registrada correctamente.")
            return redirect("entregas")
        except ValidationError as exc:
            error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        except ObjectDoesNotExist:
            error = "El comedor seleccionado no existe."
        except ValueError:
            error = "Verificá los datos ingresados (comedor, lotes, cantidades y fecha)."

    hoy = date.today()
    lotes_con_stock = deposito_services.listar_lotes(solo_con_stock=True)
    comedores = comedor_services.listar_comedores(habilitado=True)

    contexto = {
        "comedores": comedores,
        "lotes": lotes_con_stock,
        "hoy": hoy.isoformat(),
        "error": error,
    }
    return render(request, "entregas/nueva_entrega.html", contexto)