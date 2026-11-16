"""DTOs inmutables expuestos por el módulo Depósito."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ProductoDTO:
    id: int
    nombre: str


@dataclass(frozen=True)
class LoteDTO:
    id: int
    numero_lote: str
    fecha_vencimiento: date
    stock: int
    nombre_voluntario: str
    producto_id: int
    nombre_producto: str
