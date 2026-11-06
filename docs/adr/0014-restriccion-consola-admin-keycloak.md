# ADR-14: Restricción de la consola de administración de Keycloak

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 08 (tensiona 01 y 02)

## Contexto
Publicar el puerto 8080 de Keycloak a toda la red local expone, junto al login de los usuarios, la consola de administración y la API de administración (`/admin`). NFR-08 pide permisos por rol y acceso controlado.

## Decisión
Un proxy nginx (`keycloak-proxy`) delante de Keycloak, con dos puertos hacia el mismo Keycloak:
- **8080** (red local): login de usuarios; `/admin` responde 403.
- **8081** (publicado solo en `127.0.0.1` del servidor): acceso completo, incluida la consola.

Keycloak se configura con `KC_HOSTNAME` (URL pública), `KC_HOSTNAME_ADMIN=http://localhost:8081` y `KC_PROXY_HEADERS=xforwarded`, y deja de publicar puertos. La aplicación sigue hablando con Keycloak por la red interna de Docker.

No se bloquea `/realms/master`: la consola de administración emite sus tokens por los endpoints del frontend, y bloquearlo la rompería.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Dejar expuesto, con contraseña fuerte y detección de fuerza bruta | Sin componentes nuevos | La superficie de administración queda abierta a la red |
| Firewall del host | Sin contenedor extra | Filtra por puerto, no por ruta: no separa login de administración |
| Lista de IPs permitidas en un solo puerto | Un solo puerto | La IP de origen de localhost depende de cómo Docker traduce las direcciones: poco confiable |
| Administrar solo por línea de comandos (`kcadm`) | Sin consola web | Menos accesible para un voluntario |

## Consecuencias
- Un contenedor más (liviano) y una configuración sensible a las cabeceras `X-Forwarded-*`.
- Administrar Keycloak requiere estar en el servidor (`http://localhost:8081/admin/`) o usar un túnel hacia ese puerto.
- El formulario de login del realm `master` sigue visible desde la red, aunque desde allí no se puede usar la consola ni la API de administración. Conviene una contraseña robusta y habilitar la detección de fuerza bruta en ese realm.
- Si el proxy falla, tampoco funciona el login de usuarios; se acepta por NFR-09.
- Hay que actualizar el C4 de contenedores con el nuevo `keycloak-proxy`.
