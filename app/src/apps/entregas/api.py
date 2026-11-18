"""Endpoints HTTP (Django Ninja) para Entregas y DetalleEntrega. Delego la lógica en `services.py`."""

from datetime import date, datetime
from typing import Optional

from ninja import Router, Schema

from . import services

router = Router()


# --- Schemas ---
class DetalleEntregaItemIn(Schema):
    lote_id: int
    cantidad: int


class DetalleEntregaCreateIn(Schema):
    entrega_id: int
    lote_id: int
    cantidad: int


class DetalleEntregaUpdateIn(Schema):
    lote_id: Optional[int] = None
    cantidad: Optional[int] = None


class DetalleEntregaOut(Schema):
    id: int
    entrega_id: int
    lote_id: int
    cantidad: int


class EntregaIn(Schema):
    # El voluntario sale de la sesión y el estado inicial es siempre "registrada".
    fecha: date
    comedor_id: int
    detalles: Optional[list[DetalleEntregaItemIn]] = None


class EntregaUpdateIn(Schema):
    # El estado y la confirmación no se modifican por acá: la recepción la confirma
    # el referente desde su pantalla (confirmar_recepcion).
    fecha: Optional[date] = None
    comedor_id: Optional[int] = None


class EntregaOut(Schema):
    id: int
    fecha: date
    estado: str
    fecha_registro: Optional[datetime]
    fecha_confirmacion: Optional[datetime]
    nombre_voluntario: str
    comedor_id: int
    detalles: list[DetalleEntregaOut]


# --- Endpoints de DetalleEntrega ---
@router.get(
    "/detalles",
    response=list[DetalleEntregaOut],
    summary="Listar detalles de entrega",
)
def listar_detalles_entrega(
    request,
    entrega_id: Optional[int] = None,
    lote_id: Optional[int] = None,
):
    return services.listar_detalles_entrega(entrega_id=entrega_id, lote_id=lote_id)


@router.get(
    "/detalles/{detalle_id}",
    response=DetalleEntregaOut,
    summary="Obtener un detalle de entrega por ID",
)
def obtener_detalle_entrega(request, detalle_id: int):
    return services.obtener_detalle_entrega(detalle_id)


@router.post(
    "/detalles",
    response={201: DetalleEntregaOut},
    summary="Agregar un detalle a una entrega",
)
def crear_detalle_entrega(request, payload: DetalleEntregaCreateIn):
    return 201, services.crear_detalle_entrega(**payload.model_dump())


@router.put(
    "/detalles/{detalle_id}",
    response=DetalleEntregaOut,
    summary="Actualizar un detalle de entrega",
)
def actualizar_detalle_entrega(
    request, detalle_id: int, payload: DetalleEntregaUpdateIn
):
    return services.actualizar_detalle_entrega(
        detalle_id,
        **payload.model_dump(exclude_unset=True),
    )


@router.delete(
    "/detalles/{detalle_id}",
    response={204: None},
    summary="Eliminar un detalle de entrega",
)
def eliminar_detalle_entrega(request, detalle_id: int):
    services.eliminar_detalle_entrega(detalle_id)
    return 204, None


# --- Endpoints de Entrega ---
@router.get("/", response=list[EntregaOut], summary="Listar entregas")
def listar_entregas(
    request,
    comedor_id: Optional[int] = None,
    estado: Optional[str] = None,
):
    return services.listar_entregas(comedor_id=comedor_id, estado=estado)


@router.get("/{entrega_id}", response=EntregaOut, summary="Obtener una entrega por ID")
def obtener_entrega(request, entrega_id: int):
    return services.obtener_entrega(entrega_id)


@router.post("/", response={201: EntregaOut}, summary="Registrar una nueva entrega")
def crear_entrega(request, payload: EntregaIn):
    datos = payload.model_dump()
    datos["nombre_voluntario"] = request.user.get_full_name() or request.user.username
    return 201, services.crear_entrega(**datos)


@router.put("/{entrega_id}", response=EntregaOut, summary="Actualizar una entrega")
def actualizar_entrega(request, entrega_id: int, payload: EntregaUpdateIn):
    return services.actualizar_entrega(
        entrega_id,
        **payload.model_dump(exclude_unset=True),
    )


@router.delete("/{entrega_id}", response={204: None}, summary="Eliminar una entrega")
def eliminar_entrega(request, entrega_id: int):
    services.eliminar_entrega(entrega_id)
    return 204, None
