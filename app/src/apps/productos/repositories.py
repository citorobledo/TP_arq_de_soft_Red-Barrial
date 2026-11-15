"""Capa de acceso a datos (ORM) para Producto."""

from .models import Producto


def listar():
    """Devuelve todos los productos ordenados por nombre."""
    return Producto.objects.all()


def obtener_por_id(producto_id: int, *, bloquear: bool = False) -> Producto:
    """Obtiene un producto por su ID o lanza Producto.DoesNotExist."""
    qs = Producto.objects.select_for_update() if bloquear else Producto.objects.all()
    return qs.get(pk=producto_id)


def guardar(producto: Producto) -> Producto:
    """Valida las restricciones del modelo y persiste el producto en SQLite."""
    producto.full_clean()
    producto.save()
    return producto


def eliminar(producto: Producto) -> None:
    """Elimina la instancia de Producto de la base de datos."""
    producto.delete()
