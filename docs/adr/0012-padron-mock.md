# ADR-12: padron-mock como servicio simulado

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 04, 05

## Contexto
El dominio pide simular el padrón provincial como una API REST lenta que a veces no responde.

## Decisión
Un servicio FastAPI (`padron-mock`) en el Compose, con latencia aleatoria (0,2 a 7 s) y 20 % de fallas, ambas configurables por variables de entorno. Incluye 8 comedores, uno de ellos no habilitado. Swagger UI en `/docs`.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Datos fijos en la aplicación | Sin servicio extra | No permite probar timeouts ni caídas |
| Stubs solo en los tests | Rápido | No sirve para probar el sistema completo |

## Consecuencias
- Permite probar NFR-05 de forma repetible.
- La latencia máxima (7 s) supera el timeout (5 s) a propósito.
- No refleja el contrato real del padrón; se reemplaza cambiando `PADRON_URL`.
