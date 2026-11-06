# ADR-09: Autenticación OIDC con Keycloak

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 08 (tensiona 01 y 02)

## Contexto
NFR-08 exige autenticación y permisos por rol. Hay tres roles: voluntario de depósito, referente de comedor y coordinador.

## Decisión
Keycloak como proveedor OIDC. La aplicación valida el ID token con las claves públicas (JWKS), toma los roles de `realm_access.roles` del access token y los refleja como grupos de Django en cada login. La app no maneja contraseñas. El realm (roles y cliente `red-barrial-web`) se importa al iniciar.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Usuarios locales de Django | Sin contenedor extra; menos memoria y operación | Autenticación a cargo de la app |
| Otro proveedor OIDC liviano | Menor consumo | Menos conocido; otra herramienta a aprender |

## Consecuencias
- Consumo de memoria mayor que el resto del sistema junto (heap limitado a 768 MB) y un segundo almacén de datos.
- Keycloak corre en `start-dev` con H2: válido para uso local, no recomendado para producción; riesgo aceptado, a revisar si el sistema se expone.
- Sin HTTPS, el login y los tokens viajan sin cifrar dentro de la red local; riesgo aceptado porque el sistema es local y sin salida al exterior.
- La consola de administración queda restringida al servidor (ADR-14).
- El realm se importa solo la primera vez; los cambios posteriores se hacen en la consola de Keycloak.
- Los cambios de rol se reflejan en el siguiente login.
- Al depender solo del estándar OIDC, el proveedor es reemplazable.
