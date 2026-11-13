"""Casos de uso y reglas de negocio para Comedor (independientes de HTTP y del ORM)."""

from typing import Optional

from django.db import transaction

from . import repositories
from .models import Comedor


# --- GET (Lectura) ---
def listar_comedores(*, usuario_id: Optional[int] = None):
    """Lista comedores con filtro opcional por usuario referente."""
    return repositories.listar(usuario_id=usuario_id)


def obtener_comedor(comedor_id: int) -> Comedor:
    """Obtiene un comedor por su ID."""
    return repositories.obtener_por_id(comedor_id)


def obtener_comedor_por_codigo(codigo: str) -> Comedor:
    """Obtiene un comedor por su código del padrón."""
    return repositories.obtener_por_codigo(codigo.strip())


# --- POST (Creación) ---
@transaction.atomic
def crear_comedor(
    *,
    nombre: str,
    codigo: str,
    direccion: str,
    usuario_id: int,
) -> Comedor:
    """Crea un nuevo comedor validando sus datos."""
    comedor = Comedor(
        nombre=nombre.strip(),
        codigo=codigo.strip(),
        direccion=direccion.strip(),
        usuario_id=usuario_id,
    )
    repositories.guardar(comedor)
    return repositories.obtener_por_id(comedor.id)


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_comedor(
    comedor_id: int,
    *,
    nombre: Optional[str] = None,
    codigo: Optional[str] = None,
    direccion: Optional[str] = None,
    usuario_id: Optional[int] = None,
) -> Comedor:
    """Actualiza los campos provistos de un comedor existente."""
    comedor = repositories.obtener_por_id(comedor_id, bloquear=True)
    if nombre is not None:
        comedor.nombre = nombre.strip()
    if codigo is not None:
        comedor.codigo = codigo.strip()
    if direccion is not None:
        comedor.direccion = direccion.strip()
    if usuario_id is not None:
        comedor.usuario_id = usuario_id

    repositories.guardar(comedor)
    return repositories.obtener_por_id(comedor.id)


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_comedor(comedor_id: int) -> None:
    """Elimina un comedor por ID (lanza ProtectedError si tiene entregas asociadas)."""
    comedor = repositories.obtener_por_id(comedor_id, bloquear=True)
    repositories.eliminar(comedor)
