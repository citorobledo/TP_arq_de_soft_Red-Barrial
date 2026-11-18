# ADR-17: Acceso remoto del referente con un túnel ngrok

- **Estado:** Propuesto
- **Fecha:** 2026-11-18
- **NFR:** 08 (tensiona 01, 02 y 09)

## Contexto
Un referente de comedor debe poder confirmar la recepción de mercadería desde su celular, fuera de la red del depósito (ADR-11). El sistema corre en una PC local y el escenario no garantiza una IP pública ni acceso al router. Esta etapa es un trabajo práctico: no es un entorno de producción.

## Decisión
- **Modo 1:** todos los usuarios, incluido el depósito, acceden por una única URL pública `https://<dominio>.ngrok-free.app`, entregada por un túnel ngrok. Hay una sola configuración OIDC (`PUBLIC_URL`).
- El túnel es **opcional** (perfil de Compose `publico`) y apunta únicamente al puerto 8090 del proxy. La app, Keycloak, el padrón simulado y SQLite no se publican directamente; SQLite además no es un servicio de red.
- El puerto 8090 aplica **denegado por defecto**: solo pasan `/`, `/oidc/`, `/panel/`, `/comedor/`, `/deposito/`, `/entregas/`, `/coordinador/`, `/static/`, `/realms/` y `/resources/`. `/admin` responde 403 y todo lo demás, 404. Las pantallas nuevas se agregan a esa lista de forma explícita.
- La API REST (`/api/`) **no se expone** por el túnel: la interfaz web no la usa, y además exige sesión y rol.
- Límite de peticiones por IP real del cliente en el proxy, y detección de fuerza bruta en Keycloak.
- ngrok termina HTTPS; Django y Keycloak se configuran para confiar en `X-Forwarded-Proto` y en el dominio público.
- La pantalla del referente es una página dentro de la misma app Django (`/comedor/`); no se agrega un `bff-mobile`.
- Los secretos del `.env` se definen por entorno; `.env.example` solo lleva marcadores.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| VPN (Tailscale o WireGuard) | Sin exposición pública | Cada referente instala y mantiene la VPN |
| DDNS + redirección de puerto + certificado propio | Sin terceros | Requiere IP pública (CGNAT lo impide) y abre un puerto del router |
| Hosting barato (VPS con Compose) | Acceso remoto natural; no depende de la PC del depósito | Costo mensual; los datos salen del depósito |
| `bff-mobile` + API interna | Expone solo lo mínimo | Requiere otra API y otro servicio; sin cliente móvil no se justifica |
| Modo 2 (depósito por la red local, referentes por el túnel) | Funciona sin internet y permite lista de rutas solo para lo público | Hostname dinámico en Keycloak y endpoints OIDC por petición en la app |

## Consecuencias
- Sin internet o sin el túnel, **nadie puede iniciar sesión**, tampoco el depósito (NFR-09). Riesgo aceptado para esta etapa.
- ngrok termina HTTPS en su borde: el tráfico pasa descifrado por un tercero.
- Plan gratuito: un único dominio, topes mensuales de peticiones y ancho de banda (verificar las cifras vigentes) y una página de advertencia en el navegador. No es apto para producción.
- El login del realm `master` queda visible desde internet; la consola de administración sigue bloqueada, pero su inicio de sesión usa la URL pública, por lo que administrar Keycloak requiere el túnel activo. Por eso las credenciales de administrador deben ser propias y robustas.
- Con acceso remoto, el referente solo debe ver y confirmar entregas de su comedor (autorización por objeto en los servicios).
- La lista de rutas permitidas hay que mantenerla al agregar pantallas; una ruta olvidada devuelve 404 desde internet.
- Evolución prevista: modo 2, otro proveedor de túnel, VPN o VPS, y un BFF solo si aparece un cliente móvil que consuma JSON.
