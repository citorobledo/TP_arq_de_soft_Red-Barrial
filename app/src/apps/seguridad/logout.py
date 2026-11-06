from urllib.parse import urlencode

from django.conf import settings


def keycloak_logout_url(request):
    """URL de cierre de sesión en Keycloak (se invoca antes de cerrar la sesión de Django)."""
    parametros = {
        "client_id": settings.OIDC_RP_CLIENT_ID,
        "post_logout_redirect_uri": request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL),
    }
    id_token = request.session.get("oidc_id_token")
    if id_token:
        parametros["id_token_hint"] = id_token
    return f"{settings.OIDC_OP_LOGOUT_ENDPOINT}?{urlencode(parametros)}"
