"""Capa de acceso a datos (ORM) para Entrega y DetalleEntrega."""

from typing import Optional

from .models import DetalleEntrega, Entrega


# ============================================================================
# ENTREGA — Repositorio ORM
# ============================================================================
def listar_entregas(
    *,
    comedor_id: Optional[int] = None,
    estado: Optional[str] = None,
):
    """Lista entregas precargando comedor y detalles con lote/producto."""
    qs = Entrega.objects.select_related("comedor").prefetch_related(
        "detalles__lote__producto"
    )
    if comedor_id is not None:
        qs = qs.filter(comedor_id=comedor_id)
    if estado is not None:
        qs = qs.filter(estado=estado)
    return qs


def obtener_entrega_por_id(entrega_id: int, *, bloquear: bool = False) -> Entrega:
    """Obtiene una entrega por su ID o lanza Entrega.DoesNotExist."""
    if bloquear:
        return Entrega.objects.select_for_update().get(pk=entrega_id)
    return (
        Entrega.objects.select_related("comedor")
        .prefetch_related("detalles__lote__producto")
        .get(pk=entrega_id)
    )


def guardar_entrega(entrega: Entrega) -> Entrega:
    """Valida las restricciones del modelo y persiste la entrega en SQLite."""
    entrega.full_clean()
    entrega.save()
    return entrega


def eliminar_entrega(entrega: Entrega) -> None:
    """Elimina la instancia de Entrega de la base de datos."""
    entrega.delete()


# ============================================================================
# DETALLE ENTREGA — Repositorio ORM
# ============================================================================
def listar_detalles(
    *,
    entrega_id: Optional[int] = None,
    lote_id: Optional[int] = None,
    bloquear: bool = False,
):
    """Lista renglones de entrega con filtros opcionales."""
    qs = (
        DetalleEntrega.objects.select_for_update()
        if bloquear
        else DetalleEntrega.objects.select_related("lote__producto", "entrega")
    )
    if entrega_id is not None:
        qs = qs.filter(entrega_id=entrega_id)
    if lote_id is not None:
        qs = qs.filter(lote_id=lote_id)
    return qs


def obtener_detalle_por_id(detalle_id: int, *, bloquear: bool = False) -> DetalleEntrega:
    """Obtiene un detalle de entrega por su ID o lanza DetalleEntrega.DoesNotExist."""
    qs = (
        DetalleEntrega.objects.select_for_update().select_related("entrega")
        if bloquear
        else DetalleEntrega.objects.select_related("lote__producto", "entrega")
    )
    return qs.get(pk=detalle_id)


def guardar_detalle(detalle: DetalleEntrega) -> DetalleEntrega:
    """Valida las restricciones del modelo y persiste el detalle en SQLite."""
    detalle.full_clean()
    detalle.save()
    return detalle


def eliminar_detalle(detalle: DetalleEntrega) -> None:
    """Elimina la instancia de DetalleEntrega de la base de datos."""
    detalle.delete()
