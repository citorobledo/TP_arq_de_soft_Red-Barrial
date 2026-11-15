"""Casos de uso y reglas de negocio para Entrega y DetalleEntrega (Clean Architecture).

- No depende de vistas ni de HTTP.
- No ejecuta consultas ORM directas: delega la persistencia en `repositories.py`.
- Respeta los límites modulares (ADR-01): interactúa con el stock únicamente a través de `apps.deposito.services`.
"""

from datetime import date, datetime
from typing import Iterable, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.deposito import services as deposito_services

from . import repositories
from .models import DetalleEntrega, Entrega


# ============================================================================
# ENTREGA — Casos de Uso (GET, POST, PUT, DELETE)
# ============================================================================

# --- GET (Lectura) ---
def listar_entregas(
    *,
    comedor_id: Optional[int] = None,
    estado: Optional[str] = None,
):
    """Lista entregas con filtro opcional por comedor y estado."""
    return repositories.listar_entregas(comedor_id=comedor_id, estado=estado)


def obtener_entrega(entrega_id: int) -> Entrega:
    """Obtiene una entrega por su ID con comedor y detalles precargados."""
    return repositories.obtener_entrega_por_id(entrega_id)


# --- POST (Creación) ---
@transaction.atomic
def crear_entrega(
    *,
    fecha: date,
    nombre_voluntario: str,
    comedor_id: int,
    estado: str = Entrega.Estado.REGISTRADA,
    detalles: Optional[Iterable[dict]] = None,
) -> Entrega:
    """Crea una entrega y sus renglones descontando stock de forma atómica.

    Cada elemento de `detalles` debe tener la forma: `{"lote_id": int, "cantidad": int}`.
    """
    entrega = Entrega(
        fecha=fecha,
        estado=estado,
        nombre_voluntario=nombre_voluntario.strip(),
        comedor_id=comedor_id,
    )
    repositories.guardar_entrega(entrega)

    if detalles:
        for item in detalles:
            crear_detalle_entrega(
                entrega_id=entrega.id,
                lote_id=item["lote_id"],
                cantidad=item["cantidad"],
            )

    return repositories.obtener_entrega_por_id(entrega.id)


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_entrega(
    entrega_id: int,
    *,
    fecha: Optional[date] = None,
    estado: Optional[str] = None,
    fecha_confirmacion: Optional[datetime] = None,
    nombre_voluntario: Optional[str] = None,
    comedor_id: Optional[int] = None,
) -> Entrega:
    """Actualiza una entrega aplicando las reglas de transición de estados (ADR-11)."""
    entrega = repositories.obtener_entrega_por_id(entrega_id, bloquear=True)
    estado_anterior = entrega.estado

    if fecha is not None:
        entrega.fecha = fecha
    if nombre_voluntario is not None:
        entrega.nombre_voluntario = nombre_voluntario.strip()
    if comedor_id is not None:
        entrega.comedor_id = comedor_id
    if fecha_confirmacion is not None:
        entrega.fecha_confirmacion = fecha_confirmacion

    if estado is not None and estado != estado_anterior:
        if estado_anterior == Entrega.Estado.ANULADA:
            raise ValidationError("No se puede cambiar el estado de una entrega anulada.")
        entrega.estado = estado
        if estado == Entrega.Estado.CONFIRMADA and entrega.fecha_confirmacion is None:
            entrega.fecha_confirmacion = timezone.now()
        elif estado == Entrega.Estado.ANULADA:
            for detalle in repositories.listar_detalles(
                entrega_id=entrega.id, bloquear=True
            ):
                deposito_services.restituir_stock(detalle.lote_id, detalle.cantidad)

    repositories.guardar_entrega(entrega)
    return repositories.obtener_entrega_por_id(entrega.id)


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_entrega(entrega_id: int) -> None:
    """Elimina una entrega y sus detalles, restituyendo el stock si no estaba anulada."""
    entrega = repositories.obtener_entrega_por_id(entrega_id, bloquear=True)
    if entrega.estado != Entrega.Estado.ANULADA:
        for detalle in repositories.listar_detalles(
            entrega_id=entrega.id, bloquear=True
        ):
            deposito_services.restituir_stock(detalle.lote_id, detalle.cantidad)
    repositories.eliminar_entrega(entrega)


# ============================================================================
# DETALLE ENTREGA — Casos de Uso (GET, POST, PUT, DELETE)
# ============================================================================

# --- GET (Lectura) ---
def listar_detalles_entrega(
    *,
    entrega_id: Optional[int] = None,
    lote_id: Optional[int] = None,
):
    """Lista los renglones de entrega por entrega o por lote."""
    return repositories.listar_detalles(entrega_id=entrega_id, lote_id=lote_id)


def obtener_detalle_entrega(detalle_id: int) -> DetalleEntrega:
    """Obtiene un detalle de entrega por su ID."""
    return repositories.obtener_detalle_por_id(detalle_id)


# --- POST (Creación) ---
@transaction.atomic
def crear_detalle_entrega(
    *,
    entrega_id: int,
    lote_id: int,
    cantidad: int,
) -> DetalleEntrega:
    """Agrega un renglón a una entrega y descuenta el stock mediante el servicio de Lote."""
    if cantidad <= 0:
        raise ValidationError({"cantidad": "La cantidad debe ser mayor a cero."})

    entrega = repositories.obtener_entrega_por_id(entrega_id, bloquear=True)
    if entrega.estado != Entrega.Estado.ANULADA:
        deposito_services.descontar_stock(lote_id, cantidad)

    detalle = DetalleEntrega(
        entrega_id=entrega.id,
        lote_id=lote_id,
        cantidad=cantidad,
    )
    repositories.guardar_detalle(detalle)
    return repositories.obtener_detalle_por_id(detalle.id)


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_detalle_entrega(
    detalle_id: int,
    *,
    cantidad: Optional[int] = None,
    lote_id: Optional[int] = None,
) -> DetalleEntrega:
    """Actualiza lote o cantidad de un detalle reajustando el stock a través de `lote.services`."""
    detalle = repositories.obtener_detalle_por_id(detalle_id, bloquear=True)
    nuevo_lote_id = lote_id if lote_id is not None else detalle.lote_id
    nueva_cantidad = cantidad if cantidad is not None else detalle.cantidad

    if nueva_cantidad <= 0:
        raise ValidationError({"cantidad": "La cantidad debe ser mayor a cero."})

    if detalle.entrega.estado != Entrega.Estado.ANULADA:
        deposito_services.restituir_stock(detalle.lote_id, detalle.cantidad)
        deposito_services.descontar_stock(nuevo_lote_id, nueva_cantidad)

    detalle.lote_id = nuevo_lote_id
    detalle.cantidad = nueva_cantidad
    repositories.guardar_detalle(detalle)
    return repositories.obtener_detalle_por_id(detalle.id)


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_detalle_entrega(detalle_id: int) -> None:
    """Elimina un renglón de entrega y restituye su stock si la entrega no estaba anulada."""
    detalle = repositories.obtener_detalle_por_id(detalle_id, bloquear=True)
    if detalle.entrega.estado != Entrega.Estado.ANULADA:
        deposito_services.restituir_stock(detalle.lote_id, detalle.cantidad)
    repositories.eliminar_detalle(detalle)
