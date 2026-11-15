"""Capa de acceso a datos (ORM) para Comedor."""

from typing import Optional

from .models import Comedor


def listar(*, usuario_id: Optional[int] = None):
    """Lista comedores ordenados por nombre, precargando el usuario referente."""
    qs = Comedor.objects.select_related("usuario").all()
    if usuario_id is not None:
        qs = qs.filter(usuario_id=usuario_id)
    return qs


def obtener_por_id(comedor_id: int, *, bloquear: bool = False) -> Comedor:
    """Obtiene un comedor por su ID o lanza Comedor.DoesNotExist."""
    qs = Comedor.objects.select_for_update() if bloquear else Comedor.objects.select_related("usuario")
    return qs.get(pk=comedor_id)


def obtener_por_codigo(codigo: str) -> Comedor:
    """Obtiene un comedor por su código del padrón o lanza Comedor.DoesNotExist."""
    return Comedor.objects.select_related("usuario").get(codigo=codigo)


def guardar(comedor: Comedor) -> Comedor:
    """Valida las restricciones del modelo y persiste el comedor en SQLite."""
    comedor.full_clean()
    comedor.save()
    return comedor


def eliminar(comedor: Comedor) -> None:
    """Elimina la instancia de Comedor de la base de datos."""
    comedor.delete()
