"""Panel del coordinador: ve todo y exporta reportes."""

import csv
from datetime import date

from django.http import HttpResponse
from django.shortcuts import render

from apps.seguridad.decorators import rol_requerido
from apps.seguridad.roles import COORDINADOR

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
    """Único lugar donde se obtienen los datos del coordinador.

    Todavía no hay consultas conectadas a los servicios, así que devuelve vacío.
    Cada movimiento es un dict con: fecha, tipo ("ingreso" o "entrega"),
    tipo_texto, alimento, lote, cantidad, contraparte. Cada lote por vencer:
    alimento, lote, vence. Cada comedor: nombre, direccion, referente,
    estado ("habilitado" o "no_habilitado") y estado_texto (lo que se muestra).
    """
    return {
        "resumen": {"stock_kg": 0, "ingresos_hoy": 0, "entregas_hoy": 0, "por_vencer": 0},
        "movimientos": [],
        "lotes_por_vencer": [],
        "comedores": [],
        "reportes": [(clave, datos[0]) for clave, datos in REPORTES.items()],
    }


def _celda(valor):
    """Evita que Excel interprete como fórmula un texto que empieza con = + - @."""
    texto = "" if valor is None else str(valor)
    return "'" + texto if texto[:1] in ("=", "+", "-", "@") else texto


@rol_requerido(COORDINADOR)
def coordinador(request):
    return render(request, "reportes/coordinador.html", _datos())


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
