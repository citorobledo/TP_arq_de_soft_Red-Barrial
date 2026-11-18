"""Casos de uso y reglas de negocio para Entrega y DetalleEntrega (Clean Architecture).

- No depende de vistas ni de HTTP.
- No ejecuta consultas ORM directas: delega la persistencia en `repositories.py`.
- Respeta los límites modulares (ADR-01): interactúa con el stock únicamente a través de `apps.deposito.services`.
- Devuelve DTOs inmutables (`dtos.py`) para no exponer instancias activas del ORM fuera del módulo.
"""

from datetime import date, datetime
from typing import Iterable, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.deposito import services as deposito_services

from . import repositories
from .dtos import DetalleEntregaDTO, EntregaDTO
from .models import DetalleEntrega, Entrega

__all__ = [
    "EntregaDTO",
    "DetalleEntregaDTO",
    "listar_entregas",
    "obtener_entrega",
    "crear_entrega",
    "actualizar_entrega",
    "eliminar_entrega",
    "listar_detalles_entrega",
    "obtener_detalle_entrega",
    "crear_detalle_entrega",
    "actualizar_detalle_entrega",
    "eliminar_detalle_entrega",
    "confirmar_recepcion",
]


def _detalle_to_dto(detalle: DetalleEntrega) -> DetalleEntregaDTO:
    return DetalleEntregaDTO(
        id=detalle.id,
        entrega_id=detalle.entrega_id,
        lote_id=detalle.lote_id,
        cantidad=detalle.cantidad,
        numero_lote=detalle.lote.numero_lote,
        nombre_producto=detalle.lote.producto.nombre,
    )


def _entrega_to_dto(entrega: Entrega) -> EntregaDTO:
    return EntregaDTO(
        id=entrega.id,
        fecha=entrega.fecha,
        estado=entrega.estado,
        fecha_registro=entrega.fecha_registro,
        fecha_confirmacion=entrega.fecha_confirmacion,
        nombre_voluntario=entrega.nombre_voluntario,
        nombre_referente=entrega.nombre_referente,
        comedor_id=entrega.comedor_id,
        detalles=tuple(_detalle_to_dto(d) for d in entrega.detalles.all()),
    )


# ============================================================================
# ENTREGA — Casos de Uso (GET, POST, PUT, DELETE)
# ============================================================================

# --- GET (Lectura) ---
def listar_entregas(
    *,
    comedor_id: Optional[int] = None,
    estado: Optional[str] = None,
) -> list[EntregaDTO]:
    """Lista entregas con filtro opcional por comedor y estado."""
    return [
        _entrega_to_dto(e)
        for e in repositories.listar_entregas(comedor_id=comedor_id, estado=estado)
    ]


def obtener_entrega(entrega_id: int) -> EntregaDTO:
    """Obtiene una entrega por su ID con sus detalles."""
    return _entrega_to_dto(repositories.obtener_entrega_por_id(entrega_id))


# --- POST (Creación) ---
@transaction.atomic
def crear_entrega(
    *,
    fecha: date,
    nombre_voluntario: str,
    comedor_id: int,
    estado: str = Entrega.Estado.REGISTRADA,
    detalles: Optional[Iterable[dict]] = None,
) -> EntregaDTO:
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

    return _entrega_to_dto(repositories.obtener_entrega_por_id(entrega.id))


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
) -> EntregaDTO:
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
    return _entrega_to_dto(repositories.obtener_entrega_por_id(entrega.id))


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
) -> list[DetalleEntregaDTO]:
    """Lista los renglones de entrega por entrega o por lote."""
    return [
        _detalle_to_dto(d)
        for d in repositories.listar_detalles(entrega_id=entrega_id, lote_id=lote_id)
    ]


def obtener_detalle_entrega(detalle_id: int) -> DetalleEntregaDTO:
    """Obtiene un detalle de entrega por su ID."""
    return _detalle_to_dto(repositories.obtener_detalle_por_id(detalle_id))


# --- POST (Creación) ---
@transaction.atomic
def crear_detalle_entrega(
    *,
    entrega_id: int,
    lote_id: int,
    cantidad: int,
) -> DetalleEntregaDTO:
    """Agrega un renglón a una entrega y descuenta el stock mediante el servicio de Depósito."""
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
    return _detalle_to_dto(repositories.obtener_detalle_por_id(detalle.id))


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_detalle_entrega(
    detalle_id: int,
    *,
    cantidad: Optional[int] = None,
    lote_id: Optional[int] = None,
) -> DetalleEntregaDTO:
    """Actualiza lote o cantidad de un detalle reajustando el stock a través de `deposito.services`."""
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
    return _detalle_to_dto(repositories.obtener_detalle_por_id(detalle.id))


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_detalle_entrega(detalle_id: int) -> None:
    """Elimina un renglón de entrega y restituye su stock si la entrega no estaba anulada."""
    detalle = repositories.obtener_detalle_por_id(detalle_id, bloquear=True)
    if detalle.entrega.estado != Entrega.Estado.ANULADA:
        deposito_services.restituir_stock(detalle.lote_id, detalle.cantidad)
    repositories.eliminar_detalle(detalle)

@transaction.atomic
def confirmar_recepcion(
    entrega_id: int, *, usuario_id: int, nombre_referente: str
) -> EntregaDTO:
    """El referente del comedor confirma que recibió la entrega.

    Solo el referente del comedor destinatario puede hacerlo. Es idempotente:
    si ya estaba confirmada no se pisan la fecha ni el nombre (ADR-11).
    """
    entrega = repositories.obtener_entrega_por_id(entrega_id, bloquear=True)
    if entrega.comedor.usuario_id != usuario_id:
        raise ValidationError("La entrega no corresponde a un comedor de este referente.")
    if entrega.estado == Entrega.Estado.CONFIRMADA:
        return _entrega_to_dto(repositories.obtener_entrega_por_id(entrega.id))
    if entrega.estado != Entrega.Estado.REGISTRADA:
        raise ValidationError("Solo se puede recibir una entrega registrada.")
    nombre = nombre_referente.strip()
    if not nombre:
        raise ValidationError({"nombre_referente": "El nombre del referente es obligatorio."})

    entrega.estado = Entrega.Estado.CONFIRMADA
    entrega.fecha_confirmacion = timezone.now()
    entrega.nombre_referente = nombre
    repositories.guardar_entrega(entrega)
    return _entrega_to_dto(repositories.obtener_entrega_por_id(entrega.id))