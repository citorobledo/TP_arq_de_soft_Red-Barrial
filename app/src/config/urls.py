from django.urls import include, path

urlpatterns = [
    # Rutas de mozilla-django-oidc: /oidc/authenticate/, /oidc/callback/, /oidc/logout/
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("", include("apps.seguridad.urls")),
]
