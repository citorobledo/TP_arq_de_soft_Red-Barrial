"""Endpoints HTTP (Django Ninja) para Comedores. Delego la lógica en `services.py`."""

from typing import Optional

from ninja import Router, Schema

from . import services

router = Router()


class ComedorIn(Schema):
    nombre: str
    codigo: str
    direccion: str
    usuario_id: int


class ComedorUpdateIn(Schema):
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    direccion: Optional[str] = None
    usuario_id: Optional[int] = None


class ComedorOut(Schema):
    id: int
    nombre: str
    codigo: str
    direccion: str
    usuario_id: int


@router.get("/", response=list[ComedorOut], summary="Listar comedores")
def listar_comedores(request, usuario_id: Optional[int] = None):
    return services.listar_comedores(usuario_id=usuario_id)


@router.get("/{comedor_id}", response=ComedorOut, summary="Obtener un comedor por ID")
def obtener_comedor(request, comedor_id: int):
    return services.obtener_comedor(comedor_id)


@router.post("/", response={201: ComedorOut}, summary="Crear un comedor")
def crear_comedor(request, payload: ComedorIn):
    return 201, services.crear_comedor(**payload.model_dump())


@router.put("/{comedor_id}", response=ComedorOut, summary="Actualizar un comedor")
def actualizar_comedor(request, comedor_id: int, payload: ComedorUpdateIn):
    return services.actualizar_comedor(
        comedor_id,
        **payload.model_dump(exclude_unset=True),
    )


@router.delete("/{comedor_id}", response={204: None}, summary="Eliminar un comedor")
def eliminar_comedor(request, comedor_id: int):
    services.eliminar_comedor(comedor_id)
    return 204, None
