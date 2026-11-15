"""Casos de uso y reglas de negocio para Producto (independientes de HTTP y del ORM)."""

from django.db import transaction

from . import repositories
from .dtos import ProductoDTO
from .models import Producto

__all__ = [
    "ProductoDTO",
    "listar_productos",
    "obtener_producto",
    "crear_producto",
    "actualizar_producto",
    "eliminar_producto",
]


def _to_dto(producto: Producto) -> ProductoDTO:
    return ProductoDTO(
        id=producto.id,
        nombre=producto.nombre,
    )


# --- GET (Lectura) ---
def listar_productos() -> list[ProductoDTO]:
    """Devuelve el catálogo completo de productos."""
    return [_to_dto(p) for p in repositories.listar()]


def obtener_producto(producto_id: int) -> ProductoDTO:
    """Obtiene un producto por su ID."""
    return _to_dto(repositories.obtener_por_id(producto_id))


# --- POST (Creación) ---
@transaction.atomic
def crear_producto(*, nombre: str) -> ProductoDTO:
    """Crea un nuevo producto normalizando su nombre."""
    producto = Producto(nombre=nombre.strip())
    return _to_dto(repositories.guardar(producto))


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_producto(producto_id: int, *, nombre: str) -> ProductoDTO:
    """Actualiza el nombre de un producto existente."""
    producto = repositories.obtener_por_id(producto_id, bloquear=True)
    producto.nombre = nombre.strip()
    return _to_dto(repositories.guardar(producto))


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_producto(producto_id: int) -> None:
    """Elimina un producto (lanza ProtectedError si tiene lotes asociados)."""
    producto = repositories.obtener_por_id(producto_id, bloquear=True)
    repositories.eliminar(producto)
