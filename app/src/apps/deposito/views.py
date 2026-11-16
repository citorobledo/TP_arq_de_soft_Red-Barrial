"""Vista HTML del módulo Depósito (registro y listado de lotes)."""

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from apps.deposito import services as deposito_services
from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import VOLUNTARIO_DEPOSITO


@rol_requerido(VOLUNTARIO_DEPOSITO)
def deposito(request):
    error = None

    if request.method == "POST":
        accion = request.POST.get("accion", "crear_lote")

        if accion == "crear_producto":
            try:
                nombre = request.POST.get("nombre", "").strip()
                if not nombre:
                    raise ValidationError("El nombre del producto no puede estar vacío.")
                deposito_services.crear_producto(nombre=nombre)
                return redirect("deposito")
            except ValidationError as exc:
                error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        else:
            try:
                producto_id = int(request.POST.get("producto_id", "0"))
                voluntario = (
                    request.POST.get("nombre_voluntario", "").strip()
                    or request.user.get_full_name()
                    or request.user.username
                )
                deposito_services.crear_lote(
                    numero_lote=request.POST.get("numero_lote", ""),
                    fecha_vencimiento=date.fromisoformat(request.POST.get("vencimiento", "")),
                    stock=int(float(request.POST.get("cantidad", "0"))),
                    nombre_voluntario=voluntario,
                    producto_id=producto_id,
                )
                return redirect("deposito")
            except ValidationError as exc:
                error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
            except ValueError:
                error = "Verificá los datos ingresados (producto, cantidad y fecha de vencimiento)."

    hoy = date.today()
    limite_vencimiento = hoy + timedelta(days=7)
    lotes = deposito_services.listar_lotes()

    contexto = {
        "resumen": {
            "stock_kg": sum(l.stock for l in lotes),
            "lotes_con_stock": sum(1 for l in lotes if l.stock > 0),
            "lotes_totales": len(lotes),
            "por_vencer": sum(
                1
                for l in lotes
                if l.stock > 0 and hoy <= l.fecha_vencimiento <= limite_vencimiento
            ),
        },
        "lotes": lotes,
        "productos": deposito_services.listar_productos(),
        "hoy": hoy.isoformat(),
        "error": error,
    }
    return render(request, "deposito/deposito.html", contexto)
