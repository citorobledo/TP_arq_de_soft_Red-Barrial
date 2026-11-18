# ADR-18: Alcance de conectividad y transporte en modo local

- **Estado:** Aceptado
- **Fecha:** 2026-11-18
- **NFR:** 08, 09
- **Actualiza:** precisa el alcance de conectividad indicado en ADR-07 y ADR-09; complementa ADR-17.

## Contexto
ADR-07 y ADR-09 describen el uso local sin HTTPS y sin salida al exterior. En la configuración actual, las URLs locales usan HTTP y los servicios se comunican por la red de Docker Compose. Sin embargo, Compose no configura una red `internal` ni reglas que bloqueen el tráfico saliente; por lo tanto, que la aplicación no dependa de Internet no significa que Docker impida el acceso a Internet.

## Decisión
- En el modo local predeterminado, se mantiene HTTP para el acceso desde la computadora o la red del depósito. La autenticación y el padrón simulado se ejecutan como servicios locales de Compose.
- La ausencia de dependencia funcional de Internet en el modo local no se presenta como aislamiento de red: los contenedores pueden tener salida a Internet si el host y Docker lo permiten.
- El modo remoto opcional conserva el túnel ngrok de ADR-17. ngrok termina HTTPS y reenvía el tráfico al proxy por HTTP.
- El modo local se limita a una red de confianza; esta configuración no se considera apta para producción ni garantiza confidencialidad frente a otros equipos de la red.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| HTTPS también en la red local | Cifra las credenciales y sesiones en tránsito | Requiere administrar certificados y nombres locales |
| Bloquear técnicamente toda salida de los contenedores | Hace cumplir el aislamiento de egreso | Requiere una política de red adicional y compatibilidad específica con el túnel opcional |
| Mantener HTTP local y documentar su límite | No agrega operación al despliegue actual | El tráfico local no está cifrado y el egreso no queda bloqueado |

## Consecuencias
- En modo local, credenciales y sesiones pueden viajar sin cifrar por la red; el acceso debe restringirse a una red de confianza.
- Un firewall del host o una política de red externa es necesaria si se requiere impedir técnicamente la salida a Internet.
- El modo remoto necesita Internet y el túnel activo; sin ellos no se puede iniciar sesión por ese modo (ADR-17).
- HTTPS termina en ngrok; el tramo entre ngrok y el proxy permanece en HTTP dentro de Docker.

## Evidencia en el proyecto
- `docker-compose.yml`: URLs HTTP locales, servicios internos y perfil opcional `publico`; no configura aislamiento de egreso.
- `app/src/config/settings.py`: activa la configuración segura de proxy y cookies cuando `PUBLIC_URL` usa HTTPS.
- `keycloak-proxy/nginx.conf`: reenvía el tráfico del puerto 8090 con `X-Forwarded-Proto https`.
- `README.md`: documenta el acceso local y el modo remoto opcional.
