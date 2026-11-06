# ADR-06: Python + Django

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 02, 04

## Contexto
NFR-04 pide un solo lenguaje y pocas dependencias.

## Decisión
Python con Django para la aplicación. Dependencias: Django, gunicorn, whitenoise y mozilla-django-oidc. El `padron-mock` también usa Python (FastAPI).

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| FastAPI | OpenAPI automático | ORM, migraciones y UI a armar a mano |
| Node (Express/NestJS) | Un lenguaje si hubiera frontend aparte | Más piezas por elegir y mantener |

## Consecuencias
- ORM, migraciones, sesiones y plantillas incluidos.
- Hay que fijar versiones exactas de las dependencias y revisarlas con cada actualización.
