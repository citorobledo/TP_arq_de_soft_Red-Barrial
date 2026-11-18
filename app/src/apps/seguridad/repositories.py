"""Capa de acceso a datos (ORM) para usuarios y roles en el módulo Seguridad."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


def listar_usuarios_por_rol(rol: str):
    """Devuelve los usuarios que poseen el rol indicado, ordenados por username."""
    User = get_user_model()
    return User.objects.filter(groups__name=rol).order_by("username")


def usuario_tiene_rol(usuario_id: int, rol: str) -> bool:
    """Indica si el usuario indicado existe y posee el rol especificado."""
    User = get_user_model()
    return User.objects.filter(pk=usuario_id, groups__name=rol).exists()


def listar_roles_de_usuario(usuario_id: int) -> list[str]:
    """Devuelve los nombres de roles (grupos) asignados al usuario, ordenados."""
    return list(
        Group.objects.filter(user__id=usuario_id)
        .order_by("name")
        .values_list("name", flat=True)
        .distinct()
    )
