"""Capa de acceso a datos (ORM) para Producto y Lote en el módulo Depósito."""

from datetime import date
from typing import Optional

from .models import Lote, Producto


# ============================================================================
# PRODUCTO — Repositorio ORM
# ============================================================================
def listar_productos():
    """Devuelve todos los productos ordenados por nombre."""
    return Producto.objects.all()


def obtener_producto_por_id(producto_id: int, *, bloquear: bool = False) -> Producto:
    """Obtiene un producto por su ID o lanza Producto.DoesNotExist."""
    qs = Producto.objects.select_for_update() if bloquear else Producto.objects.all()
    return qs.get(pk=producto_id)


def guardar_producto(producto: Producto) -> Producto:
    """Valida las restricciones del modelo y persiste el producto en SQLite."""
    producto.full_clean()
    producto.save()
    return producto


def eliminar_producto(producto: Producto) -> None:
    """Elimina la instancia de Producto de la base de datos."""
    producto.delete()


# ============================================================================
# LOTE — Repositorio ORM
# ============================================================================
def listar(*, solo_con_stock: bool = False, producto_id: Optional[int] = None):
    """Lista lotes ordenados por fecha de vencimiento (FEFO), precargando Producto."""
    qs = Lote.objects.select_related("producto").all()
    if solo_con_stock:
        qs = qs.filter(stock__gt=0)
    if producto_id is not None:
        qs = qs.filter(producto_id=producto_id)
    return qs


def listar_por_vencer(desde: date, hasta: date):
    """Lista lotes con stock cuya fecha de vencimiento cae entre `desde` y `hasta`."""
    return Lote.objects.select_related("producto").filter(
        stock__gt=0,
        fecha_vencimiento__gte=desde,
        fecha_vencimiento__lte=hasta,
    )


def obtener_por_id(lote_id: int, *, bloquear: bool = False) -> Lote:
    """Obtiene un lote por su ID o lanza Lote.DoesNotExist."""
    qs = Lote.objects.select_for_update() if bloquear else Lote.objects.select_related("producto")
    return qs.get(pk=lote_id)


def guardar(lote: Lote, *, update_fields: Optional[list[str]] = None) -> Lote:
    """Valida las restricciones del modelo y persiste el lote en SQLite."""
    lote.full_clean()
    lote.save(update_fields=update_fields)
    return lote


def eliminar(lote: Lote) -> None:
    """Elimina la instancia de Lote de la base de datos."""
    lote.delete()
