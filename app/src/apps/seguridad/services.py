"""Servicios públicos del módulo Seguridad para consultar usuarios y roles sin exponer el ORM."""

from dataclasses import dataclass

from . import repositories

__all__ = [
    "UsuarioDTO",
    "listar_usuarios_por_rol",
    "usuario_tiene_rol",
    "listar_roles_de_usuario",
]


@dataclass(frozen=True)
class UsuarioDTO:
    id: int
    username: str
    nombre_completo: str


def listar_usuarios_por_rol(rol: str) -> list[UsuarioDTO]:
    """Devuelve los usuarios sincronizados desde Keycloak que poseen el rol indicado."""
    return [
        UsuarioDTO(
            id=u.id,
            username=u.username,
            nombre_completo=u.get_full_name() or u.username,
        )
        for u in repositories.listar_usuarios_por_rol(rol)
    ]


def usuario_tiene_rol(usuario_id: int, rol: str) -> bool:
    """Verifica si el usuario posee el rol de dominio indicado."""
    return repositories.usuario_tiene_rol(usuario_id, rol)


def listar_roles_de_usuario(usuario_id: int) -> list[str]:
    """Devuelve la lista ordenada de roles asignados a un usuario."""
    return repositories.listar_roles_de_usuario(usuario_id)
