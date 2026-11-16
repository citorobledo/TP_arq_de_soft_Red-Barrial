"""DTOs inmutables expuestos por el módulo Comedores."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ComedorDTO:
    id: int
    nombre: str
    codigo: str
    direccion: str
    usuario_id: int
    usuario_nombre: str = ""
