# ADR-05: Interfaz web renderizada en servidor

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 01, 02, 04

## Contexto
Un único mantenedor, con pocas horas por semana, y presupuesto casi nulo.

## Decisión
Vistas y plantillas HTML de Django renderizadas en servidor. Una API REST (documentada con OpenAPI) se agrega solo si surge una necesidad concreta.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| SPA + API REST | Interactividad | Segundo proyecto, más herramientas y dependencias |

## Consecuencias
- Menos tecnologías y menos código a mantener.
- Interactividad limitada; suficiente para formularios y listados.
- Sin API, no hay clientes externos; se evalúa si hace falta.
