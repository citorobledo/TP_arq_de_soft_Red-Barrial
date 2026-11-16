"""Servicios públicos del módulo Seguridad para consultar usuarios y roles sin exponer el ORM."""

from dataclasses import dataclass

from django.contrib.auth import get_user_model

__all__ = [
    "UsuarioDTO",
    "listar_usuarios_por_rol",
]


@dataclass(frozen=True)
class UsuarioDTO:
    id: int
    username: str
    nombre_completo: str


def listar_usuarios_por_rol(rol: str) -> list[UsuarioDTO]:
    """Devuelve los usuarios sincronizados desde Keycloak que poseen el rol indicado."""
    User = get_user_model()
    usuarios = User.objects.filter(groups__name=rol).order_by("username")
    return [
        UsuarioDTO(
            id=u.id,
            username=u.username,
            nombre_completo=u.get_full_name() or u.username,
        )
        for u in usuarios
    ]
