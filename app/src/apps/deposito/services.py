"""Casos de uso y reglas de negocio para Lote (independientes de HTTP y del ORM)."""

from datetime import date
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from . import repositories
from .models import Lote


# --- GET (Lectura) ---
def listar_lotes(*, solo_con_stock: bool = False, producto_id: Optional[int] = None):
    """Lista lotes ordenados por FEFO, con filtros opcionales de stock y producto."""
    return repositories.listar(solo_con_stock=solo_con_stock, producto_id=producto_id)


def obtener_lote(lote_id: int) -> Lote:
    """Obtiene un lote por su ID con su producto asociado."""
    return repositories.obtener_por_id(lote_id)


# --- POST (Creación) ---
@transaction.atomic
def crear_lote(
    *,
    numero_lote: str,
    fecha_vencimiento: date,
    stock: int,
    nombre_voluntario: str,
    producto_id: int,
) -> Lote:
    """Crea un nuevo lote validando sus reglas de negocio."""
    lote = Lote(
        numero_lote=numero_lote.strip(),
        fecha_vencimiento=fecha_vencimiento,
        stock=stock,
        nombre_voluntario=nombre_voluntario.strip(),
        producto_id=producto_id,
    )
    repositories.guardar(lote)
    return repositories.obtener_por_id(lote.id)


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_lote(
    lote_id: int,
    *,
    numero_lote: Optional[str] = None,
    fecha_vencimiento: Optional[date] = None,
    stock: Optional[int] = None,
    nombre_voluntario: Optional[str] = None,
    producto_id: Optional[int] = None,
) -> Lote:
    """Actualiza los campos provistos de un lote existente."""
    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    if numero_lote is not None:
        lote.numero_lote = numero_lote.strip()
    if fecha_vencimiento is not None:
        lote.fecha_vencimiento = fecha_vencimiento
    if stock is not None:
        lote.stock = stock
    if nombre_voluntario is not None:
        lote.nombre_voluntario = nombre_voluntario.strip()
    if producto_id is not None:
        lote.producto_id = producto_id

    repositories.guardar(lote)
    return repositories.obtener_por_id(lote.id)


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_lote(lote_id: int) -> None:
    """Elimina un lote por ID (lanza ProtectedError si tiene entregas asociadas)."""
    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    repositories.eliminar(lote)


# --- Reglas de Dominio de Stock (usadas por otros módulos como `entregas`) ---
@transaction.atomic
def descontar_stock(lote_id: int, cantidad: int) -> Lote:
    """Descuenta `cantidad` del stock de un lote garantizando que nunca quede en negativo."""
    if cantidad <= 0:
        raise ValidationError({"cantidad": "La cantidad a descontar debe ser mayor a cero."})

    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    if lote.stock < cantidad:
        raise ValidationError(
            {
                "cantidad": (
                    f"Stock insuficiente en el lote {lote.numero_lote} "
                    f"(disponible: {lote.stock})."
                )
            }
        )
    lote.stock -= cantidad
    return repositories.guardar(lote, update_fields=["stock"])


@transaction.atomic
def restituir_stock(lote_id: int, cantidad: int) -> Lote:
    """Restituye `cantidad` al stock de un lote (por anulación, edición o baja de entrega)."""
    if cantidad <= 0:
        raise ValidationError({"cantidad": "La cantidad a restituir debe ser mayor a cero."})

    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    lote.stock += cantidad
    return repositories.guardar(lote, update_fields=["stock"])
