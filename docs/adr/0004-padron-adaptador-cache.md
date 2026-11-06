# ADR-04: Padrón provincial: adaptador, timeout y caché

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 03, 05

## Contexto
Solo pueden recibir alimentos los comedores habilitados en el padrón provincial, una API REST lenta que a veces no responde (NFR-05).

## Decisión
El componente `padron` es un adaptador (capa anticorrupción) con:
- timeout de **5 s** y reintento acotado;
- caché persistida del último padrón válido, con su fecha;
- registro, en cada entrega, del estado de la verificación (en línea, con caché de fecha X, o pendiente).

La antigüedad máxima tolerada del caché se configura con `PADRON_CACHE_MAX_AGE_HOURS` (hoy 168 h).

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Llamada síncrona sin caché | Dato siempre fresco | Si el padrón falla, el depósito se frena |
| Rechazar la entrega si no responde | Máxima corrección | Bloquea la operación |
| Verificación asíncrona diferida | No bloquea | Más complejidad y estados |

## Consecuencias
- El depósito puede operar con el padrón caído.
- Una entrega podría hacerse a un comedor cuya habilitación cambió dentro de la ventana del caché; el riesgo se acepta y queda constancia (NFR-03).
- Pendiente de validar con el coordinador: qué hacer cuando el caché supera la antigüedad máxima.
