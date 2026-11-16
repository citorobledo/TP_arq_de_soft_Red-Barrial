"""Panel del coordinador: consulta el estado general a través de los servicios de cada módulo."""

import csv
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render

from apps.comedores import services as comedor_services
from apps.deposito import services as deposito_services
from apps.entregas import services as entrega_services
from apps.seguridad import services as seguridad_services
from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import COORDINADOR, REFERENTE_COMEDOR

# Reportes disponibles: clave -> (título, columnas, claves del diccionario de cada fila)
REPORTES = {
    "movimientos": (
        "Movimientos",
        ["Fecha", "Tipo", "Alimento", "Lote", "Kg", "Origen / destino"],
        ["fecha", "tipo_texto", "alimento", "lote", "cantidad", "contraparte"],
    ),
    "vencimientos": (
        "Lotes por vencer",
        ["Alimento", "Lote", "Vence"],
        ["alimento", "lote", "vence"],
    ),
    "comedores": (
        "Comedores",
        ["Comedor", "Dirección", "Referente", "Estado"],
        ["nombre", "direccion", "referente", "estado_texto"],
    ),
}
ORIGEN_DATOS = {
    "movimientos": "movimientos",
    "vencimientos": "lotes_por_vencer",
    "comedores": "comedores",
}


def _datos():
    """Obtiene la información del panel consumiendo únicamente los `services.py` de cada módulo."""
    hoy = date.today()
    limite_vencimiento = hoy + timedelta(days=7)

    lotes = deposito_services.listar_lotes()
    entregas = entrega_services.listar_entregas()
    comedores_dtos = comedor_services.listar_comedores()

    mapa_lotes = {l.id: l for l in lotes}
    mapa_comedores = {c.id: f"{c.codigo} - {c.nombre}" for c in comedores_dtos}

    movimientos = [
        {
            "fecha": l.fecha_ingreso,
            "tipo": "ingreso",
            "tipo_texto": "Ingreso",
            "alimento": l.nombre_producto,
            "lote": l.numero_lote,
            "cantidad": l.stock,
            "contraparte": l.nombre_donante or "Depósito",
        }
        for l in lotes
    ]

    for entrega in entregas:
        if entrega.estado == "anulada":
            continue
        destino = mapa_comedores.get(entrega.comedor_id, f"Comedor #{entrega.comedor_id}")
        for detalle in entrega.detalles:
            lote_info = mapa_lotes.get(detalle.lote_id)
            movimientos.append(
                {
                    "fecha": entrega.fecha,
                    "tipo": "entrega",
                    "tipo_texto": "Entrega",
                    "alimento": lote_info.nombre_producto if lote_info else f"Lote #{detalle.lote_id}",
                    "lote": lote_info.numero_lote if lote_info else f"#{detalle.lote_id}",
                    "cantidad": detalle.cantidad,
                    "contraparte": destino,
                }
            )

    movimientos.sort(key=lambda m: m["fecha"], reverse=True)

    lotes_por_vencer = [
        {
            "alimento": l.nombre_producto,
            "lote": l.numero_lote,
            "vence": l.fecha_vencimiento,
        }
        for l in lotes
        if l.stock > 0 and l.fecha_vencimiento >= hoy
    ][:10]

    comedores = [
        {
            "nombre": f"{c.codigo} - {c.nombre}",
            "direccion": c.direccion,
            "referente": c.usuario_nombre,
            "estado": "habilitado",
            "estado_texto": "Habilitado",
        }
        for c in comedores_dtos
    ]

    return {
        "resumen": {
            "stock_kg": sum(l.stock for l in lotes),
            "ingresos_hoy": sum(1 for l in lotes if l.fecha_ingreso == hoy),
            "entregas_hoy": sum(
                1 for e in entregas if e.fecha == hoy and e.estado != "anulada"
            ),
            "por_vencer": sum(
                1
                for l in lotes
                if l.stock > 0 and hoy <= l.fecha_vencimiento <= limite_vencimiento
            ),
        },
        "movimientos": movimientos,
        "lotes_por_vencer": lotes_por_vencer,
        "comedores": comedores,
        "referentes": seguridad_services.listar_usuarios_por_rol(REFERENTE_COMEDOR),
        "reportes": [(clave, datos[0]) for clave, datos in REPORTES.items()],
    }


def _celda(valor):
    """Evita que Excel interprete como fórmula un texto que empieza con = + - @."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto[:1] in ("=", "+", "-", "@") else texto


@rol_requerido(COORDINADOR)
def coordinador(request):
    error = None

    if request.method == "POST":
        try:
            usuario_id = int(request.POST.get("usuario_id", "0"))
            referentes_validos = {
                r.id for r in seguridad_services.listar_usuarios_por_rol(REFERENTE_COMEDOR)
            }
            if usuario_id not in referentes_validos:
                raise ValidationError(
                    "El usuario seleccionado no tiene el rol 'referente_comedor'."
                )

            comedor_services.crear_comedor(
                nombre=request.POST.get("nombre", ""),
                codigo=request.POST.get("codigo", ""),
                direccion=request.POST.get("direccion", ""),
                usuario_id=usuario_id,
            )
            return redirect("coordinador")
        except ValidationError as exc:
            error = "; ".join(exc.messages) if hasattr(exc, "messages") else str(exc)
        except ValueError:
            error = "Verificá los datos ingresados para registrar el comedor."

    contexto = _datos()
    contexto["error"] = error
    return render(request, "reportes/coordinador.html", contexto)


@rol_requerido(COORDINADOR)
def exportar_reportes(request):
    clave = request.GET.get("reporte", "movimientos")
    if clave not in REPORTES:
        clave = "movimientos"
    _, columnas, campos = REPORTES[clave]
    filas = _datos()[ORIGEN_DATOS[clave]]

    respuesta = HttpResponse(content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = (
        f'attachment; filename="reporte_{clave}_{date.today():%Y%m%d}.csv"'
    )
    respuesta.write("\ufeff")  # BOM: Excel respeta las tildes
    escritor = csv.writer(respuesta, delimiter=";")  # Excel en español separa con ;
    escritor.writerow(columnas)
    for fila in filas:
        escritor.writerow([_celda(fila.get(campo)) for campo in campos])
    return respuesta
