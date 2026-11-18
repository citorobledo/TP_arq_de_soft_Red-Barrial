"""DTOs inmutables expuestos por el módulo Entregas."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class DetalleEntregaDTO:
    id: int
    entrega_id: int
    lote_id: int
    cantidad: int
    numero_lote: str = ""
    nombre_producto: str = ""


@dataclass(frozen=True)
class EntregaDTO:
    id: int
    fecha: date
    estado: str
    fecha_registro: Optional[datetime]
    fecha_confirmacion: Optional[datetime]
    nombre_voluntario: str
    comedor_id: int
    detalles: tuple[DetalleEntregaDTO, ...]
    nombre_referente: str = ""
    comedor_codigo: str = ""
    comedor_nombre: str = ""
