# ADR-03: Ledger de movimientos append-only con FEFO

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 03, 07

## Contexto
Hoy nadie sabe qué lote fue a qué comedor ni cuándo vence. La auditoría que necesitan es poder responder ante un reclamo puntual (NFR-03), y el stock por lote no puede ser negativo (NFR-07).

## Decisión
- El stock de cada lote es **derivado**: suma de movimientos inmutables (ingreso, entrega, ajuste).
- Los movimientos no se actualizan ni se borran; las correcciones son **contramovimientos**.
- Cada movimiento registra lote, cantidad, comedor (si corresponde), fecha y usuario.
- Un movimiento que dejaría el stock en negativo se rechaza dentro de la misma transacción.
- Política de consumo **FEFO** (first expired, first out): una entrega descuenta primero del lote con vencimiento más próximo; el sistema alerta los lotes por vencer.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Saldo mutable por lote | Consulta directa | Se pierde el historial; no cumple NFR-03 |
| Event sourcing completo | Reconstrucción total | Complejidad desproporcionada para el contexto |
| FIFO / elección manual del lote | Más simple | No prioriza vencimientos |

## Consecuencias
- La auditoría sale del propio modelo de datos.
- El stock requiere agregación; con 300 movimientos por mes el costo es despreciable.
- Pendiente de validar con el coordinador: si se permite elegir un lote manualmente y con qué registro del motivo.
