"""Capa de acceso a datos (ORM) para Lote."""

from typing import Optional

from .models import Lote


def listar(*, solo_con_stock: bool = False, producto_id: Optional[int] = None):
    """Lista lotes ordenados por fecha de vencimiento (FEFO), precargando Producto."""
    qs = Lote.objects.select_related("producto").all()
    if solo_con_stock:
        qs = qs.filter(stock__gt=0)
    if producto_id is not None:
        qs = qs.filter(producto_id=producto_id)
    return qs


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
