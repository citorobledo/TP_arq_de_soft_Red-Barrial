"""Casos de uso y reglas de negocio para Producto (independientes de HTTP y del ORM)."""

from django.db import transaction

from . import repositories
from .models import Producto


# --- GET (Lectura) ---
def listar_productos():
    """Devuelve el catálogo completo de productos."""
    return repositories.listar()


def obtener_producto(producto_id: int) -> Producto:
    """Obtiene un producto por su ID."""
    return repositories.obtener_por_id(producto_id)


# --- POST (Creación) ---
@transaction.atomic
def crear_producto(*, nombre: str) -> Producto:
    """Crea un nuevo producto normalizando su nombre."""
    producto = Producto(nombre=nombre.strip())
    return repositories.guardar(producto)


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_producto(producto_id: int, *, nombre: str) -> Producto:
    """Actualiza el nombre de un producto existente."""
    producto = repositories.obtener_por_id(producto_id, bloquear=True)
    producto.nombre = nombre.strip()
    return repositories.guardar(producto)


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_producto(producto_id: int) -> None:
    """Elimina un producto (lanza ProtectedError si tiene lotes asociados)."""
    producto = repositories.obtener_por_id(producto_id, bloquear=True)
    repositories.eliminar(producto)
