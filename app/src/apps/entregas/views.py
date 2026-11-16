"""Vista HTML del módulo Entregas (registro y listado de entregas a comedores)."""

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from apps.comedores import services as comedor_services
from apps.deposito import services as deposito_services
from apps.entregas import services as entrega_services
from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import VOLUNTARIO_DEPOSITO


@rol_requerido(VOLUNTARIO_DEPOSITO)
def entregas(request):
    error = None

    if request.method == "POST":
        try:
            comedor_id = int(request.POST.get("comedor", "0"))
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
            voluntario = (
                request.POST.get("nombre_voluntario", "").strip()
                or request.user.get_full_name()
                or request.user.username
            )
            entrega_services.crear_entrega(
                fecha=fecha,
                nombre_voluntario=voluntario,
                comedor_id=comedor_id,
                detalles=detalles,
            )
            return redirect("entregas")
        except ValidationError as exc:
            error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        except ValueError:
            error = "Verificá los datos ingresados (comedor, lotes, cantidades y fecha)."

    hoy = date.today()
    limite_vencimiento = hoy + timedelta(days=7)
    todos_los_lotes = deposito_services.listar_lotes()
    lotes_con_stock = [l for l in todos_los_lotes if l.stock > 0]
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
        "resumen": {
            "stock_kg": sum(l.stock for l in todos_los_lotes),
            "ingresos_hoy": len(todos_los_lotes),
            "entregas_hoy": sum(1 for e in lista_entregas if e.fecha == hoy),
            "por_vencer": sum(
                1
                for l in todos_los_lotes
                if l.stock > 0 and hoy <= l.fecha_vencimiento <= limite_vencimiento
            ),
        },
        "entregas": entregas_vista,
        "comedores": comedores,
        "lotes": [
            {
                "id": l.id,
                "descripcion": (
                    f"{l.numero_lote} · {l.nombre_producto} "
                    f"(Stock: {l.stock} | Vence: {l.fecha_vencimiento})"
                ),
            }
            for l in lotes_con_stock
        ],
        "hoy": hoy.isoformat(),
        "error": error,
    }
    return render(request, "entregas/entregas.html", contexto)
