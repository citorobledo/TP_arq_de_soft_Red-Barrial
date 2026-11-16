"""Endpoints HTTP (Django Ninja) para Productos y Lotes de Depósito."""

from datetime import date
from typing import Optional

from ninja import Router, Schema

from . import services

router = Router()
productos_router = Router()


# ============================================================================
# PRODUCTOS
# ============================================================================
class ProductoIn(Schema):
    nombre: str


class ProductoOut(Schema):
    id: int
    nombre: str


@productos_router.get("/", response=list[ProductoOut], summary="Listar productos")
def listar_productos(request):
    return services.listar_productos()


@productos_router.get(
    "/{producto_id}", response=ProductoOut, summary="Obtener un producto por ID"
)
def obtener_producto(request, producto_id: int):
    return services.obtener_producto(producto_id)


@productos_router.post("/", response={201: ProductoOut}, summary="Crear un producto")
def crear_producto(request, payload: ProductoIn):
    return 201, services.crear_producto(nombre=payload.nombre)


@productos_router.put(
    "/{producto_id}", response=ProductoOut, summary="Actualizar un producto"
)
def actualizar_producto(request, producto_id: int, payload: ProductoIn):
    return services.actualizar_producto(producto_id, nombre=payload.nombre)


@productos_router.delete(
    "/{producto_id}", response={204: None}, summary="Eliminar un producto"
)
def eliminar_producto(request, producto_id: int):
    services.eliminar_producto(producto_id)
    return 204, None


# ============================================================================
# LOTES
# ============================================================================
class LoteIn(Schema):
    numero_lote: str
    fecha_vencimiento: date
    stock: int
    nombre_voluntario: str
    producto_id: int


class LoteUpdateIn(Schema):
    numero_lote: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    stock: Optional[int] = None
    nombre_voluntario: Optional[str] = None
    producto_id: Optional[int] = None


class LoteOut(Schema):
    id: int
    numero_lote: str
    fecha_vencimiento: date
    stock: int
    nombre_voluntario: str
    producto_id: int
    nombre_producto: str


@router.get("/", response=list[LoteOut], summary="Listar lotes (orden FEFO)")
def listar_lotes(
    request,
    solo_con_stock: bool = False,
    producto_id: Optional[int] = None,
):
    return services.listar_lotes(
        solo_con_stock=solo_con_stock,
        producto_id=producto_id,
    )


@router.get("/{lote_id}", response=LoteOut, summary="Obtener un lote por ID")
def obtener_lote(request, lote_id: int):
    return services.obtener_lote(lote_id)


@router.post("/", response={201: LoteOut}, summary="Registrar un nuevo lote")
def crear_lote(request, payload: LoteIn):
    return 201, services.crear_lote(**payload.model_dump())


@router.put("/{lote_id}", response=LoteOut, summary="Actualizar un lote")
def actualizar_lote(request, lote_id: int, payload: LoteUpdateIn):
    return services.actualizar_lote(
        lote_id,
        **payload.model_dump(exclude_unset=True),
    )


@router.delete("/{lote_id}", response={204: None}, summary="Eliminar un lote")
def eliminar_lote(request, lote_id: int):
    services.eliminar_lote(lote_id)
    return 204, None
