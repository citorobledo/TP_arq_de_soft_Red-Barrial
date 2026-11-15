"""Endpoints HTTP (Django Ninja) para Productos. Delego la lógica en `services.py`."""

from ninja import Router, Schema

from . import services

router = Router()


class ProductoIn(Schema):
    nombre: str


class ProductoOut(Schema):
    id: int
    nombre: str


@router.get("/", response=list[ProductoOut], summary="Listar productos")
def listar_productos(request):
    return services.listar_productos()


@router.get("/{producto_id}", response=ProductoOut, summary="Obtener un producto por ID")
def obtener_producto(request, producto_id: int):
    return services.obtener_producto(producto_id)


@router.post("/", response={201: ProductoOut}, summary="Crear un producto")
def crear_producto(request, payload: ProductoIn):
    return 201, services.crear_producto(nombre=payload.nombre)


@router.put("/{producto_id}", response=ProductoOut, summary="Actualizar un producto")
def actualizar_producto(request, producto_id: int, payload: ProductoIn):
    return services.actualizar_producto(producto_id, nombre=payload.nombre)


@router.delete("/{producto_id}", response={204: None}, summary="Eliminar un producto")
def eliminar_producto(request, producto_id: int):
    services.eliminar_producto(producto_id)
    return 204, None
