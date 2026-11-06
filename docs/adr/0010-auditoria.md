# ADR-10: Auditoría: anulación lógica y log

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 03

## Contexto
Ningún movimiento se borra ni se modifica (NFR-03).

## Decisión
- No hay borrado físico: lo erróneo se **anula** con un registro que referencia al original.
- Cada operación escribe un registro de auditoría (usuario, fecha, acción, entidad) en la misma transacción que la operación.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Borrado físico | Simple | Destruye evidencia |
| Triggers en la base | Captura todo | Lógica fuera del código y de los tests |
| Librería de historial | Menos código propio | Dependencia adicional |

## Consecuencias
- Las tablas crecen; con 300 movimientos por mes es irrelevante.
- Las consultas deben distinguir registros anulados.
