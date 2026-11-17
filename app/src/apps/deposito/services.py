"""Casos de uso y reglas de negocio para Producto y Lote (independientes de HTTP y del ORM)."""

from datetime import date, timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from . import repositories
from .dtos import LoteDTO, ProductoDTO
from .models import Lote, Producto

__all__ = [
    "ProductoDTO",
    "LoteDTO",
    "listar_productos",
    "obtener_producto",
    "crear_producto",
    "actualizar_producto",
    "eliminar_producto",
    "listar_lotes",
    "listar_lotes_por_vencer",
    "obtener_lote",
    "crear_lote",
    "actualizar_lote",
    "eliminar_lote",
    "descontar_stock",
    "restituir_stock",
]


def _producto_to_dto(producto: Producto) -> ProductoDTO:
    return ProductoDTO(
        id=producto.id,
        nombre=producto.nombre,
    )


def _to_dto(lote: Lote) -> LoteDTO:
    return LoteDTO(
        id=lote.id,
        numero_lote=lote.numero_lote,
        fecha_ingreso=lote.fecha_ingreso,
        fecha_vencimiento=lote.fecha_vencimiento,
        stock=lote.stock,
        nombre_voluntario=lote.nombre_voluntario,
        nombre_donante=lote.nombre_donante,
        producto_id=lote.producto_id,
        nombre_producto=lote.producto.nombre,
    )


# ============================================================================
# PRODUCTO — Casos de Uso (GET, POST, PUT, DELETE)
# ============================================================================
def listar_productos() -> list[ProductoDTO]:
    """Devuelve el catálogo completo de productos."""
    return [_producto_to_dto(p) for p in repositories.listar_productos()]


def obtener_producto(producto_id: int) -> ProductoDTO:
    """Obtiene un producto por su ID."""
    return _producto_to_dto(repositories.obtener_producto_por_id(producto_id))


@transaction.atomic
def crear_producto(*, nombre: str) -> ProductoDTO:
    """Crea un nuevo producto normalizando su nombre."""
    producto = Producto(nombre=nombre.strip())
    return _producto_to_dto(repositories.guardar_producto(producto))


@transaction.atomic
def actualizar_producto(producto_id: int, *, nombre: str) -> ProductoDTO:
    """Actualiza el nombre de un producto existente."""
    producto = repositories.obtener_producto_por_id(producto_id, bloquear=True)
    producto.nombre = nombre.strip()
    return _producto_to_dto(repositories.guardar_producto(producto))


@transaction.atomic
def eliminar_producto(producto_id: int) -> None:
    """Elimina un producto (lanza ProtectedError si tiene lotes asociados)."""
    producto = repositories.obtener_producto_por_id(producto_id, bloquear=True)
    repositories.eliminar_producto(producto)


# ============================================================================
# LOTE — Casos de Uso (GET, POST, PUT, DELETE)
# ============================================================================
def listar_lotes(
    *,
    solo_con_stock: bool = False,
    producto_id: Optional[int] = None,
) -> list[LoteDTO]:
    """Lista lotes ordenados por FEFO, con filtros opcionales de stock y producto."""
    return [
        _to_dto(lote)
        for lote in repositories.listar(
            solo_con_stock=solo_con_stock, producto_id=producto_id
        )
    ]


def listar_lotes_por_vencer(
    *,
    dias: int = 7,
    hoy: Optional[date] = None,
) -> list[LoteDTO]:
    """Lista lotes con stock disponible que vencen dentro de los próximos `dias` días."""
    fecha_base = hoy if hoy is not None else date.today()
    limite = fecha_base + timedelta(days=dias)
    return [
        _to_dto(lote)
        for lote in repositories.listar_por_vencer(fecha_base, limite)
    ]


def obtener_lote(lote_id: int) -> LoteDTO:
    """Obtiene un lote por su ID con su producto asociado."""
    return _to_dto(repositories.obtener_por_id(lote_id))


@transaction.atomic
def crear_lote(
    *,
    numero_lote: str,
    fecha_vencimiento: date,
    stock: int,
    nombre_voluntario: str,
    producto_id: int,
    nombre_donante: str = "",
    fecha_ingreso: Optional[date] = None,
) -> LoteDTO:
    """Crea un nuevo lote validando sus reglas de negocio."""
    lote = Lote(
        numero_lote=numero_lote.strip(),
        fecha_vencimiento=fecha_vencimiento,
        stock=stock,
        nombre_voluntario=nombre_voluntario.strip(),
        nombre_donante=nombre_donante.strip(),
        producto_id=producto_id,
    )
    if fecha_ingreso is not None:
        lote.fecha_ingreso = fecha_ingreso
    repositories.guardar(lote)
    return _to_dto(repositories.obtener_por_id(lote.id))


@transaction.atomic
def actualizar_lote(
    lote_id: int,
    *,
    numero_lote: Optional[str] = None,
    fecha_ingreso: Optional[date] = None,
    fecha_vencimiento: Optional[date] = None,
    stock: Optional[int] = None,
    nombre_voluntario: Optional[str] = None,
    nombre_donante: Optional[str] = None,
    producto_id: Optional[int] = None,
) -> LoteDTO:
    """Actualiza los campos provistos de un lote existente."""
    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    if numero_lote is not None:
        lote.numero_lote = numero_lote.strip()
    if fecha_ingreso is not None:
        lote.fecha_ingreso = fecha_ingreso
    if fecha_vencimiento is not None:
        lote.fecha_vencimiento = fecha_vencimiento
    if stock is not None:
        lote.stock = stock
    if nombre_voluntario is not None:
        lote.nombre_voluntario = nombre_voluntario.strip()
    if nombre_donante is not None:
        lote.nombre_donante = nombre_donante.strip()
    if producto_id is not None:
        lote.producto_id = producto_id

    repositories.guardar(lote)
    return _to_dto(repositories.obtener_por_id(lote.id))


@transaction.atomic
def eliminar_lote(lote_id: int) -> None:
    """Elimina un lote por ID (lanza ProtectedError si tiene entregas asociadas)."""
    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    repositories.eliminar(lote)


# --- Reglas de Dominio de Stock (usadas por otros módulos como `entregas`) ---
@transaction.atomic
def descontar_stock(lote_id: int, cantidad: int) -> LoteDTO:
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
    repositories.guardar(lote, update_fields=["stock"])
    return _to_dto(repositories.obtener_por_id(lote.id))


@transaction.atomic
def restituir_stock(lote_id: int, cantidad: int) -> LoteDTO:
    """Restituye `cantidad` al stock de un lote (por anulación, edición o baja de entrega)."""
    if cantidad <= 0:
        raise ValidationError({"cantidad": "La cantidad a restituir debe ser mayor a cero."})

    lote = repositories.obtener_por_id(lote_id, bloquear=True)
    lote.stock += cantidad
    repositories.guardar(lote, update_fields=["stock"])
    return _to_dto(repositories.obtener_por_id(lote.id))
