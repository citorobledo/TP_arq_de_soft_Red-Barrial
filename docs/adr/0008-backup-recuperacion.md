# ADR-08: Backup y recuperación

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 01, 06

## Contexto
NFR-06 exige RPO ≤ 2 días y RTO ≤ 4 h. La PC donada puede fallar.

## Decisión
- Respaldo **diario** programado con cron del host (por ejemplo, de madrugada): `scripts/backup.sh`.
- SQLite se copia en caliente con la API de backup; Keycloak (H2) se detiene unos segundos para copiar sin riesgo de corrupción.
- Retención: los últimos 14 respaldos.
- Restauración con `scripts/restore.sh <carpeta>`, que pide confirmación explícita.

La frecuencia diaria deja margen de una ejecución fallida dentro del RPO de 2 días (un respaldo cada 48 h sería el mínimo, sin tolerancia a fallos).

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Respaldo manual | Sin automatización | Depende de que alguien se acuerde |
| Cada 2 días | Cumple el RPO justo | Una falla incumple NFR-06 |
| Replicación continua | RPO casi nulo | Excede el contexto |

## Consecuencias
- Corte de Keycloak de unos segundos en cada respaldo, en horario sin operación.
- Los respaldos en el mismo disco no protegen de una falla del disco: se recomienda copiar periódicamente a un medio externo.
- Hay que probar la restauración periódicamente para sostener el RTO de 4 h.
