"""Configuración central de la API REST con Django Ninja, OpenAPI y errores RFC 9457."""

from http import HTTPStatus
from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import ProtectedError
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError

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


def _problem_response(
    request,
    *,
    status: int,
    title: str,
    detail: str,
    problem_type: str = "about:blank",
    errors: Optional[Any] = None,
):
    """Construye una respuesta de error conforme a RFC 9457 (application/problem+json)."""
    payload: dict[str, Any] = {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.get_full_path(),
    }
    if errors is not None:
        payload["errors"] = errors

    response = api.create_response(request, payload, status=status)
    response["Content-Type"] = "application/problem+json"
    return response


@api.exception_handler(ObjectDoesNotExist)
def handle_not_found(request, exc):
    return _problem_response(
        request,
        status=404,
        problem_type="urn:red-barrial:error:no-encontrado",
        title="Recurso no encontrado",
        detail="El recurso solicitado no existe.",
    )


@api.exception_handler(ValidationError)
def handle_domain_validation_error(request, exc):
    errors = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
    return _problem_response(
        request,
        status=400,
        problem_type="urn:red-barrial:error:validacion",
        title="Error de validación",
        detail="Uno o más campos incumplen las reglas de validación del dominio.",
        errors=errors,
    )


@api.exception_handler(ProtectedError)
def handle_protected_error(request, exc):
    return _problem_response(
        request,
        status=409,
        problem_type="urn:red-barrial:error:conflicto-integridad",
        title="Conflicto de integridad",
        detail="No se puede eliminar el recurso porque está referenciado por otros registros.",
    )


@api.exception_handler(NinjaValidationError)
def handle_ninja_validation_error(request, exc):
    return _problem_response(
        request,
        status=422,
        problem_type="urn:red-barrial:error:esquema-invalido",
        title="Error de validación de entrada",
        detail="El cuerpo o los parámetros de la solicitud no cumplen el esquema esperado.",
        errors=exc.errors,
    )


@api.exception_handler(HttpError)
def handle_http_error(request, exc):
    try:
        title = HTTPStatus(exc.status_code).phrase
    except ValueError:
        title = "Error HTTP"
    return _problem_response(
        request,
        status=exc.status_code,
        problem_type="about:blank",
        title=title,
        detail=exc.message,
    )


api.add_router("/productos", productos_router, tags=["Productos"])
api.add_router("/lotes", deposito_router, tags=["Depósito / Lotes"])
api.add_router("/comedores", comedores_router, tags=["Comedores"])
api.add_router("/entregas", entregas_router, tags=["Entregas"])
