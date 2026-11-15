"""DTOs inmutables expuestos por el módulo Productos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductoDTO:
    id: int
    nombre: str
