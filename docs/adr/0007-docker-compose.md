# ADR-07: Despliegue con Docker Compose

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 01, 09

## Contexto
Un voluntario debe poder desplegar o reiniciar el sistema con un único comando (NFR-01). Debe volver a levantar solo tras un corte de luz (NFR-09).

## Decisión
Docker Compose con los servicios `app`, `keycloak`, `keycloak-proxy` (ADR-14) y `padron-mock`, volúmenes `app-data` y `keycloak-data`, `restart: unless-stopped` y configuración por `.env`. Arranque: `docker compose up -d --build`.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Instalación manual | Sin Docker | Frágil y poco reproducible |
| Kubernetes | Orquestación completa | Excesivo para el contexto |
| PaaS | Operación delegada | Costo recurrente; contradice NFR-02 |

## Consecuencias
- La PC debe tener Docker instalado.
- Los servicios se reinician solos tras un corte.
- Sin HTTPS: el sistema es local y sin salida al exterior.
