"""Simulación del padrón provincial de comedores habilitados.

API REST deliberadamente poco confiable (latencia variable y fallas
aleatorias), como describe el dominio. Se configura con variables de entorno.
"""
import asyncio
import os
import random

from fastapi import FastAPI, HTTPException

LATENCIA_MIN = float(os.getenv("MOCK_LATENCY_MIN", "0.2"))
LATENCIA_MAX = float(os.getenv("MOCK_LATENCY_MAX", "7.0"))
TASA_FALLAS = float(os.getenv("MOCK_FAILURE_RATE", "0.2"))

app = FastAPI(title="Padrón provincial (simulado)", version="0.1.0")

COMEDORES = {
    "CP-001": {"nombre": "Comedor Los Pibes", "habilitado": True},
    "CP-002": {"nombre": "Merendero La Esperanza", "habilitado": True},
    "CP-003": {"nombre": "Comedor San Cayetano", "habilitado": True},
    "CP-004": {"nombre": "Olla Popular Barrio Norte", "habilitado": True},
    "CP-005": {"nombre": "Comedor Manos Unidas", "habilitado": True},
    "CP-006": {"nombre": "Merendero El Trébol", "habilitado": True},
    "CP-007": {"nombre": "Comedor Nuevo Amanecer", "habilitado": True},
    "CP-008": {"nombre": "Comedor Sin Habilitación", "habilitado": False},
}


async def simular_condiciones() -> None:
    """Demora aleatoria y, a veces, error 503 (el padrón 'no responde')."""
    await asyncio.sleep(random.uniform(LATENCIA_MIN, LATENCIA_MAX))
    if random.random() < TASA_FALLAS:
        raise HTTPException(status_code=503, detail="Padrón no disponible")


@app.get("/health", include_in_schema=False)
async def health() -> dict:
    return {"status": "ok"}


@app.get("/comedores")
async def listar_comedores() -> list[dict]:
    await simular_condiciones()
    return [{"codigo": c, **datos} for c, datos in COMEDORES.items()]


@app.get("/comedores/{codigo}")
async def obtener_comedor(codigo: str) -> dict:
    await simular_condiciones()
    if codigo not in COMEDORES:
        raise HTTPException(status_code=404, detail="Comedor no registrado")
    return {"codigo": codigo, **COMEDORES[codigo]}
