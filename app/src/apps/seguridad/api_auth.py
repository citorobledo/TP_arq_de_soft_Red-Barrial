"""Autenticación de la API REST: sesión iniciada (vía Keycloak) + rol permitido."""
from ninja.errors import HttpError
from ninja.security import SessionAuth


class AuthPorRol(SessionAuth):
    """401 si no hay sesión; 403 si el usuario no tiene ninguno de los roles indicados.

    Los roles de Keycloak se reflejan como grupos de Django al iniciar sesión
    (ver backends.py). SessionAuth exige además el token CSRF en POST, PUT y DELETE.
    """

    def __init__(self, *roles):
        super().__init__()
        self.roles = set(roles)

    def authenticate(self, request, key):
        usuario = super().authenticate(request, key)
        if usuario is None:
            return None
        if not usuario.groups.filter(name__in=self.roles).exists():
            raise HttpError(403, "Tu rol no permite usar la API.")
        return usuario
