from django.urls import include, path

from .api import api

urlpatterns = [
    # Rutas de mozilla-django-oidc: /oidc/authenticate/, /oidc/callback/, /oidc/logout/
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("api/", api.urls),
    path("", include("apps.seguridad.urls")),
]
