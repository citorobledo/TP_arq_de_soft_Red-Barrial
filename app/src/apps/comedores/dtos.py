"""DTOs inmutables expuestos por el módulo Comedores."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ComedorDTO:
    id: int
    nombre: str
    codigo: str
    direccion: str
    usuario_id: Optional[int]
    habilitado: bool
    usuario_nombre: str = ""
