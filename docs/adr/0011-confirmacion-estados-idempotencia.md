# ADR-11: Confirmación por estados e idempotencia

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 03, 07

## Contexto
El voluntario registra la entrega y el referente del comedor confirma lo recibido. Un doble clic o un reintento no debe duplicar el descuento de stock (NFR-07).

## Decisión
- Estados de la entrega: `registrada` → `confirmada` (o `anulada`).
- El stock se descuenta al **registrar** (caso de uso mínimo del dominio); la confirmación no lo modifica.
- El registro es idempotente: cada formulario lleva una clave de operación única y una repetición se ignora.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Un solo paso, sin confirmación | Más simple | No queda evidencia de lo recibido |
| Confirmación fuera del sistema | Sin desarrollo | Vuelve a las planillas |

## Consecuencias
- Queda evidencia de cada entrega y de su confirmación.
- Pendiente de validar con el coordinador: qué ocurre si el referente discrepa o no confirma.
