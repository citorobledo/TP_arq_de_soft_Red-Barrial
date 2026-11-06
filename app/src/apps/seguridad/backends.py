"""Backend OIDC para Keycloak.

- Los datos del usuario salen del ID token (ya verificado con JWKS), sin llamar
  al endpoint userinfo.
- Los roles salen de `realm_access.roles` del access token, que la app recibe
  directamente del endpoint de tokens.
- Cada rol de Keycloak se refleja como un Group de Django (se sincroniza en cada login).
"""
import base64
import json

from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from .roles import ROLES


def roles_desde_access_token(access_token):
    try:
        carga = access_token.split(".")[1]
        carga += "=" * (-len(carga) % 4)
        datos = json.loads(base64.urlsafe_b64decode(carga))
    except (IndexError, ValueError):
        return []
    return [r for r in datos.get("realm_access", {}).get("roles", []) if r in ROLES]


class KeycloakOIDCBackend(OIDCAuthenticationBackend):
    def get_userinfo(self, access_token, id_token, payload):
        claims = dict(payload)
        claims["roles"] = roles_desde_access_token(access_token)
        return claims

    def verify_claims(self, claims):
        return bool(claims.get("preferred_username"))

    def filter_users_by_claims(self, claims):
        username = claims.get("preferred_username")
        if not username:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(username__iexact=username)

    def create_user(self, claims):
        user = self.UserModel.objects.create_user(
            username=claims["preferred_username"],
            email=claims.get("email", ""),
            first_name=claims.get("given_name", ""),
            last_name=claims.get("family_name", ""),
        )
        self._sincronizar_roles(user, claims)
        return user

    def update_user(self, user, claims):
        user.email = claims.get("email", user.email)
        user.first_name = claims.get("given_name", user.first_name)
        user.last_name = claims.get("family_name", user.last_name)
        user.save()
        self._sincronizar_roles(user, claims)
        return user

    @staticmethod
    def _sincronizar_roles(user, claims):
        grupos = [Group.objects.get_or_create(name=r)[0] for r in claims.get("roles", [])]
        user.groups.set(grupos)
