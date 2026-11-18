# ADR-19: Operación efectiva de respaldos y recuperación

- **Estado:** Aceptado
- **Fecha:** 2026-11-18
- **NFR:** 06
- **Actualiza:** precisa la operación vigente de ADR-08; no elimina sus objetivos de RPO y RTO.

## Contexto
ADR-08 propone ejecutar respaldos diarios mediante cron. El repositorio incluye los scripts `scripts/backup.sh` y `scripts/restore.sh`, pero no incorpora una configuración de cron ni otro planificador. La documentación de uso indica ejecutar los scripts manualmente desde la raíz del proyecto.

## Decisión
- Hasta que se configure un planificador en el host, el respaldo se ejecuta manualmente con `bash scripts/backup.sh`.
- Se conserva la implementación del script: SQLite se copia en caliente con su API de respaldo, Keycloak se detiene temporalmente para copiar H2 y se conservan los últimos 14 respaldos.
- La restauración se ejecuta manualmente con `bash scripts/restore.sh <directorio>` y exige confirmar la operación escribiendo `si`.
- El RPO de dos días de NFR-06 solo se cumple si el operador ejecuta respaldos con la frecuencia necesaria. El repositorio, por sí solo, no garantiza esa frecuencia.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Ejecución manual | No requiere servicios adicionales ni permisos de administración del host | Depende de que el operador recuerde hacer el respaldo |
| Programador del host (cron o equivalente) | Permite automatizar una frecuencia diaria | Requiere configurar y supervisar el host donde se ejecuta Compose |

## Consecuencias
- El respaldo se puede generar y restaurar con las herramientas del proyecto, pero no se ejecuta automáticamente.
- Para sostener el RPO, quien administra el host debe programar y comprobar los respaldos.
- El RTO de cuatro horas no queda verificado hasta que se pruebe una restauración en el entorno de despliegue.
- Los respaldos guardados en el mismo disco no protegen ante la pérdida de ese disco, como ya advierte ADR-08.

## Evidencia en el proyecto
- `scripts/backup.sh`: copia SQLite en caliente, detiene Keycloak para copiar H2 y conserva 14 directorios.
- `scripts/restore.sh`: solicita confirmación, restaura los volúmenes y reinicia los servicios.
- `README.md`: proporciona comandos manuales y no configura un planificador.
