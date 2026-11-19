# ADR-20: Autenticación de administración de Keycloak solo local

- **Estado:** Aceptado
- **Fecha:** 2026-11-18
- **NFR:** 08
- **Actualiza:** precisa ADR-14 y restringe el acceso público previsto por ADR-17.

## Contexto
Aunque ADR-14 publica la consola solo en `127.0.0.1:8081` y configura `KC_HOSTNAME_ADMIN` con esa URL, el hostname frontend global de Keycloak puede dirigir el inicio de sesión del realm `master` al dominio ngrok. Además, el proxy público permite actualmente `/realms/`, lo que incluye el endpoint de autenticación de `master`.

## Decisión
- El frontend del realm `master` se configura como `http://localhost:8081` mediante un servicio de inicialización de Compose que espera a que Keycloak esté saludable.
- El proxy deniega `/realms/master` y sus subrutas tanto en el puerto de usuarios 8080 como en la entrada pública 8090. La autenticación de `master` solo queda disponible por el puerto 8081, ligado a loopback. El acceso a `red-barrial` permanece habilitado para el inicio de sesión de la aplicación.
- El puerto de administración sigue publicado únicamente en `127.0.0.1:8081`; no se publica para otros equipos de la red ni se enruta por el túnel.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Mantener la URL pública para el login de `master` | No requiere configuración adicional | Hace accesible desde Internet el flujo de autenticación administrativa |
| Cambiar el hostname global de Keycloak a localhost | Simplifica el acceso administrativo local | Rompe el flujo OIDC público del realm `red-barrial` |
| Separar el frontend de `master` y bloquearlo en el proxy público | Conserva el OIDC público de la aplicación y limita administración al host | Agrega una inicialización de realm y reglas específicas al proxy |

## Consecuencias
- El acceso a la consola y su autenticación requieren el equipo que ejecuta Docker.
- Los puertos 8080 y 8090 conservan los endpoints necesarios para los usuarios de `red-barrial`, pero no pueden iniciar autenticación contra `master`.
- Si falla el servicio de inicialización, Compose no inicia el proxy; los logs de `keycloak-admin-realm-config` deben revisarse antes de reintentar.
- La consola usa HTTP en loopback (`localhost`), mientras que el acceso remoto de la aplicación continúa usando HTTPS terminado en ngrok.

## Evidencia en el proyecto
- `docker-compose.yml`: vincula el puerto 8081 a `127.0.0.1` y configura el frontend local de `master`.
- `keycloak-proxy/nginx.conf`: deniega el realm `master` en los puertos 8080 y 8090.
- `docs/adr/0014-restriccion-consola-admin-keycloak.md`: decisión original de restricción de la consola.
- `docs/adr/0017-acceso-remoto-ngrok.md`: decisión de acceso público por ngrok.
