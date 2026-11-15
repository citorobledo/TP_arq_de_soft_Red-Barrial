"""Configuración central de la API REST con Django Ninja y documentación OpenAPI automática."""

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import ProtectedError
from ninja import NinjaAPI

from apps.comedores.api import router as comedores_router
from apps.deposito.api import router as deposito_router
from apps.entregas.api import router as entregas_router
from apps.productos.api import router as productos_router

# Para exigir sesión OIDC de Keycloak en toda la API, importar `django_auth` de `ninja.security`
# y pasar `auth=django_auth` al instanciar NinjaAPI.
api = NinjaAPI(
    title="Red Barrial · Banco de Alimentos API",
    version="1.0.0",
    description="API REST para la gestión de productos, lotes de depósito, comedores y entregas.",
)


@api.exception_handler(ObjectDoesNotExist)
def handle_not_found(request, exc):
    return api.create_response(
        request,
        {"detail": "El recurso solicitado no existe."},
        status=404,
    )


@api.exception_handler(ValidationError)
def handle_validation_error(request, exc):
    detail = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
    return api.create_response(
        request,
        {"detail": detail},
        status=400,
    )


@api.exception_handler(ProtectedError)
def handle_protected_error(request, exc):
    return api.create_response(
        request,
        {"detail": "No se puede eliminar el recurso porque está referenciado por otros registros."},
        status=409,
    )


api.add_router("/productos", productos_router, tags=["Productos"])
api.add_router("/lotes", deposito_router, tags=["Depósito / Lotes"])
api.add_router("/comedores", comedores_router, tags=["Comedores"])
api.add_router("/entregas", entregas_router, tags=["Entregas"])
