"""Casos de uso y reglas de negocio para Comedor (independientes de HTTP y del ORM)."""

import json
import logging
import time
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from . import repositories
from .dtos import ComedorDTO
from .models import Comedor

logger = logging.getLogger(__name__)
PADRON_MAX_ATTEMPTS = 5

__all__ = [
    "ComedorDTO",
    "listar_comedores",
    "obtener_comedor",
    "obtener_comedor_por_codigo",
    "crear_comedor",
    "actualizar_comedor",
    "eliminar_comedor",
    "sincronizar_comedores_padron",
]


def _to_dto(comedor: Comedor) -> ComedorDTO:
    usuario_nombre = ""
    if comedor.usuario_id is not None:
        usuario_nombre = comedor.usuario.get_full_name() or comedor.usuario.username
    return ComedorDTO(
        id=comedor.id,
        nombre=comedor.nombre,
        codigo=comedor.codigo,
        direccion=comedor.direccion,
        usuario_id=comedor.usuario_id,
        habilitado=comedor.habilitado,
        usuario_nombre=usuario_nombre,
    )


def _consultar_padron() -> list[dict]:
    url = f"{settings.PADRON_URL.rstrip('/')}/comedores"
    ultimo_error = None

    for intento in range(1, PADRON_MAX_ATTEMPTS + 1):
        try:
            with urlopen(url, timeout=settings.PADRON_TIMEOUT_SECONDS) as respuesta:
                comedores = json.loads(respuesta.read().decode("utf-8"))
            if not isinstance(comedores, list):
                raise ValueError("El padrón no devolvió una lista de comedores.")
            return comedores
        except HTTPError as error:
            if error.code < 500:
                raise RuntimeError(
                    f"El padrón respondió HTTP {error.code} al listar comedores."
                ) from error
            ultimo_error = error
        except (URLError, TimeoutError) as error:
            ultimo_error = error

        if intento < PADRON_MAX_ATTEMPTS:
            logger.warning(
                "No se pudo consultar el padrón (intento %d/%d): %s",
                intento,
                PADRON_MAX_ATTEMPTS,
                ultimo_error,
            )
            time.sleep(min(intento, 3))

    raise RuntimeError(
        f"No se pudo consultar el padrón después de {PADRON_MAX_ATTEMPTS} intentos."
    ) from ultimo_error


def _normalizar_comedor_padron(datos: dict) -> dict:
    if not isinstance(datos, dict):
        raise ValueError("Cada comedor del padrón debe ser un objeto JSON.")

    normalizado = {}
    for campo in ("codigo", "nombre", "direccion"):
        valor = datos.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El comedor del padrón debe incluir {campo} no vacío.")
        normalizado[campo] = valor.strip()

    if "usuario_id" not in datos:
        raise ValueError("El comedor del padrón debe incluir usuario_id.")
    usuario_id = datos["usuario_id"]
    if usuario_id is not None and (
        type(usuario_id) is not int or usuario_id < 1
    ):
        raise ValueError("usuario_id debe ser un entero positivo o null.")
    normalizado["usuario_id"] = usuario_id
    habilitado = datos.get("habilitado")
    if not isinstance(habilitado, bool):
        raise ValueError("El comedor del padrón debe incluir habilitado como booleano.")
    normalizado["habilitado"] = habilitado
    return normalizado


def sincronizar_comedores_padron() -> dict[str, int]:
    """Inserta o actualiza los comedores publicados por el padrón provincial."""
    datos_padron = _consultar_padron()
    comedores = [_normalizar_comedor_padron(datos) for datos in datos_padron]

    codigos = [comedor["codigo"] for comedor in comedores]
    if len(codigos) != len(set(codigos)):
        raise ValueError("El padrón devolvió códigos de comedor duplicados.")

    User = get_user_model()
    usuario_ids = {
        comedor["usuario_id"]
        for comedor in comedores
        if comedor["usuario_id"] is not None
    }
    usuarios_existentes = set(
        User.objects.filter(pk__in=usuario_ids).values_list("pk", flat=True)
    )
    insertados = 0
    actualizados = 0
    with transaction.atomic():
        for datos in comedores:
            usuario_id = datos["usuario_id"]
            if usuario_id is not None and usuario_id not in usuarios_existentes:
                logger.warning(
                    "El usuario_id %s del comedor %s no existe; se importará sin referente.",
                    usuario_id,
                    datos["codigo"],
                )
                usuario_id = None
            _, creado = Comedor.objects.update_or_create(
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "direccion": datos["direccion"],
                    "habilitado": datos["habilitado"],
                    "usuario_id": usuario_id,
                },
            )
            if creado:
                insertados += 1
            else:
                actualizados += 1

    return {"insertados": insertados, "actualizados": actualizados}


# --- GET (Lectura) ---
def listar_comedores(*, usuario_id: Optional[int] = None) -> list[ComedorDTO]:
    """Lista comedores con filtro opcional por usuario referente."""
    return [_to_dto(c) for c in repositories.listar(usuario_id=usuario_id)]


def obtener_comedor(comedor_id: int) -> ComedorDTO:
    """Obtiene un comedor por su ID."""
    return _to_dto(repositories.obtener_por_id(comedor_id))


def obtener_comedor_por_codigo(codigo: str) -> ComedorDTO:
    """Obtiene un comedor por su código del padrón."""
    return _to_dto(repositories.obtener_por_codigo(codigo.strip()))


# --- POST (Creación) ---
@transaction.atomic
def crear_comedor(
    *,
    nombre: str,
    codigo: str,
    direccion: str,
    usuario_id: int,
) -> ComedorDTO:
    """Crea un nuevo comedor validando sus datos."""
    comedor = Comedor(
        nombre=nombre.strip(),
        codigo=codigo.strip(),
        direccion=direccion.strip(),
        usuario_id=usuario_id,
    )
    repositories.guardar(comedor)
    return _to_dto(repositories.obtener_por_id(comedor.id))


# --- PUT (Actualización) ---
@transaction.atomic
def actualizar_comedor(
    comedor_id: int,
    *,
    nombre: Optional[str] = None,
    codigo: Optional[str] = None,
    direccion: Optional[str] = None,
    usuario_id: Optional[int] = None,
) -> ComedorDTO:
    """Actualiza los campos provistos de un comedor existente."""
    comedor = repositories.obtener_por_id(comedor_id, bloquear=True)
    if nombre is not None:
        comedor.nombre = nombre.strip()
    if codigo is not None:
        comedor.codigo = codigo.strip()
    if direccion is not None:
        comedor.direccion = direccion.strip()
    if usuario_id is not None:
        comedor.usuario_id = usuario_id

    repositories.guardar(comedor)
    return _to_dto(repositories.obtener_por_id(comedor.id))


# --- DELETE (Eliminación) ---
@transaction.atomic
def eliminar_comedor(comedor_id: int) -> None:
    """Elimina un comedor por ID (lanza ProtectedError si tiene entregas asociadas)."""
    comedor = repositories.obtener_por_id(comedor_id, bloquear=True)
    repositories.eliminar(comedor)
