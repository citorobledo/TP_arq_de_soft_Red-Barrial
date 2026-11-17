"""Panel del coordinador: consulta el estado general y exporta reportes CSV."""

import csv
from datetime import date, timedelta
from typing import Optional

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
    "ingresos": (
        "Ingresos",
        ["Fecha ingreso", "Alimento", "Lote", "Stock", "Donante", "Voluntario"],
        ["fecha", "alimento", "lote", "cantidad", "contraparte", "voluntario"],
    ),
    "entregas": (
        "Entregas",
        ["Fecha", "Comedor", "Alimento", "Lote", "Cantidad", "Estado", "Voluntario"],
        ["fecha", "contraparte", "alimento", "lote", "cantidad", "estado", "voluntario"],
    ),
    "movimientos": (
        "Todos los movimientos",
        ["Fecha", "Tipo", "Alimento", "Lote", "Cantidad", "Origen / destino"],
        ["fecha", "tipo_texto", "alimento", "lote", "cantidad", "contraparte"],
    ),
    "vencimientos": (
        "Lotes por vencer (próximos 7 días)",
        ["Alimento", "Lote", "Vence", "Stock", "Donante"],
        ["alimento", "lote", "vence", "stock", "donante"],
    ),
    "comedores": (
        "Comedores",
        ["Comedor", "Dirección", "Referente", "Estado"],
        ["nombre", "direccion", "referente", "estado_texto"],
    ),
}
ORIGEN_DATOS = {
    "ingresos": "ingresos",
    "entregas": "entregas_reporte",
    "movimientos": "movimientos",
    "vencimientos": "lotes_por_vencer_7d",
    "comedores": "comedores",
}
REPORTES_CON_FECHA = {"ingresos", "entregas", "movimientos"}


def _parse_fecha(valor: str) -> Optional[date]:
    texto = (valor or "").strip()
    if not texto:
        return None
    try:
        return date.fromisoformat(texto)
    except ValueError:
        return None


def _filtrar_por_fecha(filas: list[dict], desde: Optional[date], hasta: Optional[date]) -> list[dict]:
    resultado = filas
    if desde is not None:
        resultado = [f for f in resultado if f["fecha"] >= desde]
    if hasta is not None:
        resultado = [f for f in resultado if f["fecha"] <= hasta]
    return resultado


def _datos():
    """Obtiene la información del panel consumiendo únicamente los `services.py` de cada módulo."""
    hoy = date.today()
    limite_vencimiento = hoy + timedelta(days=7)

    lotes = deposito_services.listar_lotes()
    entregas = entrega_services.listar_entregas()
    comedores_dtos = comedor_services.listar_comedores()

    mapa_lotes = {l.id: l for l in lotes}
    mapa_comedores = {c.id: f"{c.codigo} - {c.nombre}" for c in comedores_dtos}

    ingresos = [
        {
            "fecha": l.fecha_ingreso,
            "tipo": "ingreso",
            "tipo_texto": "Ingreso",
            "alimento": l.nombre_producto,
            "lote": l.numero_lote,
            "cantidad": l.stock,
            "contraparte": l.nombre_donante or "Depósito",
            "voluntario": l.nombre_voluntario,
        }
        for l in lotes
    ]
    ingresos.sort(key=lambda m: m["fecha"], reverse=True)

    entregas_reporte = []
    for entrega in entregas:
        destino = mapa_comedores.get(entrega.comedor_id, f"Comedor #{entrega.comedor_id}")
        for detalle in entrega.detalles:
            lote_info = mapa_lotes.get(detalle.lote_id)
            entregas_reporte.append(
                {
                    "fecha": entrega.fecha,
                    "tipo": "entrega",
                    "tipo_texto": "Entrega",
                    "alimento": lote_info.nombre_producto if lote_info else f"Lote #{detalle.lote_id}",
                    "lote": lote_info.numero_lote if lote_info else f"#{detalle.lote_id}",
                    "cantidad": detalle.cantidad,
                    "contraparte": destino,
                    "estado": entrega.estado,
                    "voluntario": entrega.nombre_voluntario,
                }
            )
    entregas_reporte.sort(key=lambda m: m["fecha"], reverse=True)

    movimientos = ingresos + [
        e for e in entregas_reporte if e["estado"] != "anulada"
    ]
    movimientos.sort(key=lambda m: m["fecha"], reverse=True)

    lotes_por_vencer_7d = [
        {
            "alimento": l.nombre_producto,
            "lote": l.numero_lote,
            "vence": l.fecha_vencimiento,
            "stock": l.stock,
            "donante": l.nombre_donante or "—",
        }
        for l in lotes
        if l.stock > 0 and hoy <= l.fecha_vencimiento <= limite_vencimiento
    ]

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
            "estado": "habilitado" if c.habilitado else "no_habilitado",
            "estado_texto": "Habilitado" if c.habilitado else "No habilitado",
        }
        for c in comedores_dtos
    ]

    entregas_tabla = [
        {
            "id": e.id,
            "fecha": e.fecha,
            "comedor": mapa_comedores.get(e.comedor_id, f"Comedor #{e.comedor_id}"),
            "estado": e.estado,
            "fecha_registro": e.fecha_registro,
            "fecha_confirmacion": e.fecha_confirmacion,
            "nombre_voluntario": e.nombre_voluntario,
            "nombre_referente": e.nombre_referente,
            "detalles": e.detalles,
        }
        for e in entregas
    ]

    return {
        "resumen": {
            "stock_kg": sum(l.stock for l in lotes),
            "ingresos_hoy": sum(1 for l in lotes if l.fecha_ingreso == hoy),
            "entregas_hoy": sum(
                1 for e in entregas if e.fecha == hoy and e.estado != "anulada"
            ),
            "por_vencer": len(lotes_por_vencer_7d),
        },
        "lotes_tabla": sorted(lotes, key=lambda l: (l.fecha_ingreso, l.id), reverse=True),
        "entregas_tabla": entregas_tabla,
        "ingresos": ingresos,
        "entregas_reporte": entregas_reporte,
        "movimientos": movimientos,
        "lotes_por_vencer": lotes_por_vencer,
        "lotes_por_vencer_7d": lotes_por_vencer_7d,
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

    if clave in REPORTES_CON_FECHA:
        desde = _parse_fecha(request.GET.get("desde", ""))
        hasta = _parse_fecha(request.GET.get("hasta", ""))
        filas = _filtrar_por_fecha(filas, desde, hasta)

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
