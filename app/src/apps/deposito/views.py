"""Vista HTML del módulo Depósito (registro y listado de lotes)."""

from datetime import date

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import ProtectedError
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
                messages.success(request, f"Producto «{nombre}» agregado al catálogo.")
                return redirect("deposito")
            except ValidationError as exc:
                error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        elif accion == "editar_lote":
            try:
                lote_id = int(request.POST.get("lote_id", "0"))
                producto_id = int(request.POST.get("producto_id", "0"))
                fecha_ingreso_str = request.POST.get("fecha_ingreso", "").strip()
                fecha_ingreso = (
                    date.fromisoformat(fecha_ingreso_str) if fecha_ingreso_str else None
                )
                voluntario = (
                    request.POST.get("nombre_voluntario", "").strip()
                    or request.user.get_full_name()
                    or request.user.username
                )
                deposito_services.actualizar_lote(
                    lote_id,
                    numero_lote=request.POST.get("numero_lote", ""),
                    fecha_ingreso=fecha_ingreso,
                    fecha_vencimiento=date.fromisoformat(
                        request.POST.get("vencimiento", "")
                    ),
                    stock=int(float(request.POST.get("cantidad", "0"))),
                    nombre_voluntario=voluntario,
                    nombre_donante=request.POST.get("nombre_donante", ""),
                    producto_id=producto_id,
                )
                messages.success(request, "Lote actualizado correctamente.")
                return redirect("deposito")
            except ObjectDoesNotExist:
                error = "El lote seleccionado no existe."
            except ValidationError as exc:
                error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
            except ValueError:
                error = "Verificá los datos ingresados para editar el lote."
        elif accion == "eliminar_lote":
            try:
                lote_id = int(request.POST.get("lote_id", "0"))
                deposito_services.eliminar_lote(lote_id)
                messages.success(request, "Lote eliminado.")
                return redirect("deposito")
            except ObjectDoesNotExist:
                error = "El lote seleccionado no existe."
            except ProtectedError:
                error = "No se puede eliminar este lote porque está asociado a una o más entregas."
            except ValueError:
                error = "Identificador de lote inválido."
        else:
            try:
                producto_id = int(request.POST.get("producto_id", "0"))
                fecha_ingreso_str = request.POST.get("fecha_ingreso", "").strip()
                fecha_ingreso = (
                    date.fromisoformat(fecha_ingreso_str) if fecha_ingreso_str else None
                )
                voluntario = request.user.get_full_name() or request.user.username
                numero_lote = request.POST.get("numero_lote", "")
                deposito_services.crear_lote(
                    numero_lote=numero_lote,
                    fecha_ingreso=fecha_ingreso,
                    fecha_vencimiento=date.fromisoformat(request.POST.get("vencimiento", "")),
                    stock=int(float(request.POST.get("cantidad", "0"))),
                    nombre_voluntario=voluntario,
                    nombre_donante=request.POST.get("nombre_donante", ""),
                    producto_id=producto_id,
                )
                messages.success(request, f"Lote {numero_lote} agregado correctamente.")
                return redirect("deposito")
            except ValidationError as exc:
                error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
            except ValueError:
                error = "Verificá los datos ingresados (producto, cantidad y fecha de vencimiento)."

    hoy = date.today()
    lotes = deposito_services.listar_lotes()
    lotes_por_vencer = deposito_services.listar_lotes_por_vencer(hoy=hoy)

    contexto = {
        "resumen": {
            "stock_kg": sum(l.stock for l in lotes),
            "lotes_con_stock": sum(1 for l in lotes if l.stock > 0),
            "lotes_totales": len(lotes),
            "por_vencer": len(lotes_por_vencer),
        },
        "lotes": lotes,
        "productos": deposito_services.listar_productos(),
        "hoy": hoy.isoformat(),
        "error": error,
    }
    return render(request, "deposito/deposito.html", contexto)