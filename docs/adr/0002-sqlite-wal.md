# ADR-02: SQLite en modo WAL

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 01, 02, 06, 07

## Contexto
Carga muy baja y presupuesto casi nulo. El stock requiere operaciones atómicas (NFR-07) y un respaldo simple (NFR-06).

## Decisión
SQLite en un único archivo dentro del volumen `app-data`, con `journal_mode=WAL` y `transaction_mode=IMMEDIATE` (Django 5.1 o superior). Solo el contenedor `app` accede al archivo.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| PostgreSQL | Más robusta ante concurrencia; herramientas de respaldo | Un contenedor más, más memoria y más operación |
| MySQL/MariaDB | Similar a PostgreSQL | Mismas desventajas |

## Consecuencias
- Respaldo copiando el archivo con la API de backup de SQLite, sin detener la app.
- Las escrituras se serializan; es suficiente para la carga prevista.
- Las transacciones ACID sostienen la atomicidad del descuento de stock.
- Si la carga o la concurrencia crecen, se revisa el cambio a PostgreSQL (el ORM de Django lo facilita).
