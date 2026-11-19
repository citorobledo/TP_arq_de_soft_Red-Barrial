# Red barrial · Banco de alimentos

Trabajo práctico de Arquitectura de Software 1. Prototipo local para una red
barrial de comedores.

> **Estado del proyecto:** la base web y la autenticación están implementadas,
> pero todavía no están desarrolladas las funciones de negocio para registrar
> donaciones, lotes o entregas. El padrón disponible es un servicio simulado;
> sus comedores se sincronizan con la aplicación al iniciar el contenedor.

## Funcionalidad disponible

- Inicio web y panel autenticado, implementados con Django y plantillas del
  servidor.
- Inicio y cierre de sesión delegados a Keycloak mediante OpenID Connect
  (OIDC).
- Sincronización de los roles de Keycloak con grupos de Django. Los roles
  configurados son `voluntario_deposito`, `referente_comedor` y `coordinador`.
- API simulada del padrón provincial, con demoras y errores configurables.
- Sincronización de comedores del padrón a SQLite al iniciar el contenedor de
  Django: actualiza solo el estado de los registros locales con código coincidente.
- Persistencia preparada con SQLite y volumen Docker; todavía no hay modelos ni
  operaciones de negocio para movimientos de alimentos.

La arquitectura y los requisitos objetivo están documentados, pero no deben
interpretarse como funcionalidades ya entregadas. En particular, aún faltan el
registro y la trazabilidad de movimientos, la integración del padrón y las
pruebas automatizadas.

## Arquitectura actual

| Componente | Tecnología y responsabilidad |
|---|---|
| Aplicación web | Django 5.1+, Python 3.12, Gunicorn y plantillas renderizadas en el servidor. |
| Identidad | Keycloak 26 por OIDC; un inicializador corrige los permisos del volumen de datos antes del arranque y un proxy Nginx bloquea la consola administrativa en el puerto de login. |
| Persistencia | SQLite en modo WAL para Django; H2 en archivo para Keycloak. Ambos datos viven en volúmenes Docker. |
| Padrón simulado | FastAPI y Uvicorn; expone endpoints REST con demoras y fallas configurables. Django sincroniza sus comedores al arrancar. |
| Orquestación | Docker Compose inicia la aplicación, Keycloak, su proxy y el mock. |

## Requisitos

- Docker Engine y Docker Compose v2.
- Para ejecutar los scripts de respaldo y restauración: Bash (Linux, macOS,
  WSL o Git Bash en Windows).

No hace falta instalar Python localmente: Django y el padrón simulado se
ejecutan en sus contenedores.

## Inicio rápido

Desde la raíz del repositorio, copiar `.env.example` a `.env` (en PowerShell,
por ejemplo):

```powershell
Copy-Item .env.example .env
```

Editar `.env` antes de iniciar:

- Reemplazar los valores `cambiar-esto` por secretos propios y robustos.
- Mantener `PUBLIC_HOST=localhost` para usar todo desde la misma computadora.

Luego, desde la raíz del repositorio:

```powershell
docker compose up -d --build
```

Compose inicializa automáticamente los permisos del volumen de Keycloak antes
de iniciar el servicio. La aplicación ejecuta las migraciones, consulta
`http://padron-mock:8001/comedores` y actualiza únicamente `habilitado` en los
comedores locales cuyo `codigo` coincide con el padrón. No crea comedores ni
cambia sus demás datos. Para detener los servicios:

```powershell
docker compose down
```

Esto conserva los datos en los volúmenes. No usar `docker compose down -v`
salvo que se quieran eliminar también esos datos.

## Acceso y configuración de usuarios

| Servicio | URL | Acceso |
|---|---|---|
| Inicio de la aplicación | http://localhost:8000/ | Página pública; desde allí se inicia sesión |
| Inicio de sesión OIDC | http://localhost:8000/oidc/authenticate/ | Inicia el redireccionamiento a Keycloak |
| Panel de la aplicación | http://localhost:8000/panel/ | Requiere iniciar sesión; muestra usuario y roles |
| Panel de voluntario deposito | http://localhost:8000/deposito/ | sesion iniciada con el rol; muestra ingreso y egreso mercaderia |
| Panel de coordinador | http://localhost:8000/cordinador/ | sesion iniciada con el rol; muestra coordinador ve todo el movimiento,prontos a vencer y exporta reportes |
| Retorno OIDC | http://localhost:8000/oidc/callback/ | URL de retorno de Keycloak; no abrir manualmente |
| Cierre de sesión OIDC | http://localhost:8000/oidc/logout/ | Se envía mediante el formulario de cierre de sesión de la aplicación |
| Consola de administración de Keycloak | http://localhost:8081/admin/ | Solo accesible desde la computadora que ejecuta Docker; autenticación del realm `master` local |
| Cuenta del realm en Keycloak | http://localhost:8080/realms/red-barrial/account/ | Acceso a la cuenta del usuario del realm |
| Configuración OIDC del realm | http://localhost:8080/realms/red-barrial/.well-known/openid-configuration | Documento JSON para comprobar que el realm responde |
| Swagger UI del padrón simulado | http://localhost:8001/docs | Sólo accesible desde la computadora que ejecuta Docker |
| Redoc del padrón simulado | http://localhost:8001/redoc | Sólo accesible desde la computadora que ejecuta Docker |
| Salud del padrón simulado | http://localhost:8001/health | Responde `{"status":"ok"}` |
| Lista de comedores de prueba | http://localhost:8001/comedores | API de ejemplo; puede demorar o responder HTTP 503 |
| Consulta de comedor de prueba | http://localhost:8001/comedores/CP-001 | API de ejemplo; puede demorar o responder HTTP 503 |
| Swagger UI de la OpenAPI | http://localhost:8000/api/docs | Documentación en la especificación OpenAPI en la interfaz visual |
| JSON de la OpenAPI | http://localhost:8000/api/openapi.json | Documentación en la especificación OpenAPI en formato JSON |

El realm `red-barrial` y el cliente OIDC `red-barrial-web` se importan al
iniciar Keycloak. No se crean usuarios automáticamente: hay que dar de alta
las cuentas y asignarles los roles del realm desde la consola administrativa.
Al iniciar sesión, el panel muestra el usuario y sus roles; todavía no hay
pantallas de negocio con permisos por rol.

Para comprobar el flujo principal, abrir `/`, iniciar sesión desde el botón
**Ingresar con Keycloak** y verificar que se vuelve al panel en `/panel/`.
Asignar previamente un rol al usuario desde la consola de administración para
verlo reflejado en el panel. La sincronización del padrón no modifica el
`usuario_id` ni los demás datos locales del comedor.

### Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| voluntario | voluntario123 | `voluntario_deposito` |
| referente | referente123 | `referente_comedor` |
| coordinador | coordinador123 | `coordinador` |

## Uso desde otras computadoras de la red

En `.env`, cambiar `PUBLIC_HOST` por la IP o el nombre de red de la computadora
que ejecuta Docker; por ejemplo, `PUBLIC_HOST=192.168.1.20`. Después, recrear
los servicios:

```powershell
docker compose up -d --build
```

Los usuarios deben acceder a `http://<PUBLIC_HOST>:8000`. El mismo valor se
utiliza para el emisor OIDC y las URLs de redirección de Keycloak. La consola
administrativa (puerto `8081`) y el padrón simulado (puerto `8001`) permanecen
limitados al equipo servidor.

## Acceso remoto con ngrok (opcional, ADR-17)

Permite que un referente de comedor entre desde su celular, fuera de la red del
depósito. Es una configuración para el trabajo práctico y demostraciones, no
para producción. Todos los usuarios, incluido el depósito, entran por la URL
pública; sin internet o sin el túnel nadie puede iniciar sesión.

1. Crear una cuenta en ngrok y copiar el *authtoken* y el dominio gratuito
   asignado.
2. **Antes de activar el modo público**, en la consola de Keycloak
   (`http://localhost:8081/admin/`, realm `red-barrial`, Clients,
   `red-barrial-web`) agregar el dominio a *Valid redirect URIs*
   (`https://<dominio>/*`), *Valid post logout redirect URIs*
   (`https://<dominio>/*`) y *Web origins* (`https://<dominio>`). El realm solo
   se importa la primera vez, por eso hay que hacerlo a mano.
3. En `.env`: `PUBLIC_HOST=<dominio sin https://>`,
   `PUBLIC_URL=https://<dominio>` y `NGROK_AUTHTOKEN=<token>`.
4. Iniciar con el perfil público:

```bash
docker compose --profile publico up -d --build
```

Solo se expone el puerto 8090 del proxy, con rutas permitidas (`/`, `/oidc/`,
`/panel/`, `/comedor/`, `/deposito/`, `/entregas/`, `/coordinador/`, `/static/`,
`/realms/` excepto `/realms/master`, `/resources/`); `/admin` y `/realms/master`
responden 403 y el resto, 404. La API REST
(`/api/`) no se expone por el túnel. Cada pantalla nueva debe agregarse a esa lista
en `keycloak-proxy/nginx.conf`, o devolverá 404 desde internet.

Antes de activar el modo público, reemplazá todos los valores `cambiar-esto` de
`.env` por secretos propios: con el túnel activo, el login de Keycloak es
alcanzable desde internet. Con el acceso remoto activo, administrar Keycloak
también requiere el túnel levantado, porque el inicio de sesión de la consola
usa la URL pública.

Para volver al uso local: vaciar `PUBLIC_URL`, volver a `PUBLIC_HOST=localhost`,
ejecutar `docker compose --profile publico stop ngrok` y luego
`docker compose up -d`.

## Variables de entorno

| Variable | Uso |
|---|---|
| `PUBLIC_HOST` | Host público de la aplicación en la red local; por defecto, `localhost`. |
| `PUBLIC_URL` | URL pública con `https://` del túnel ngrok (opcional). Vacía en uso local. |
| `NGROK_AUTHTOKEN` | Token de la cuenta de ngrok (opcional; solo con acceso remoto). |
| `KEYCLOAK_VERSION` | Versión de la imagen de Keycloak; por defecto, `26.0`. |
| `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD` | Usuario y contraseña iniciales del administrador de Keycloak. |
| `OIDC_CLIENT_SECRET` | Secreto del cliente OIDC; debe coincidir entre la configuración de Keycloak y Django. |
| `DJANGO_SECRET_KEY` | Clave secreta de Django. |
| `MOCK_LATENCY_MIN`, `MOCK_LATENCY_MAX` | Demora mínima y máxima del padrón simulado, en segundos. |
| `MOCK_FAILURE_RATE` | Probabilidad de error del padrón, entre `0` y `1`. |

No publicar el archivo `.env` ni reutilizar sus secretos en otros entornos. La
configuración usa HTTP, Keycloak en modo de desarrollo y almacenamiento H2:
está pensada para el prototipo en una red local, no para usarlo en producción.
La única exposición a Internet prevista es el túnel opcional de ngrok descrito en
la sección siguiente.

## Padrón provincial simulado

El servicio `padron-mock` ofrece:

- `GET /health`: estado del servicio, sin demora aleatoria.
- `GET /comedores`: lista de comedores de ejemplo.
- `GET /comedores/{codigo}`: consulta un comedor por código.

Los registros incluyen `codigo`, `nombre`, `direccion`, `usuario_id` y
`habilitado`. Al iniciar, Django solo consume `codigo` y `habilitado` para
actualizar el estado de los comedores locales que encuentre por código; no
crea comedores ni modifica `nombre`, `direccion` o `usuario_id`. Los códigos
sin coincidencia se ignoran. Las consultas al padrón pueden demorarse y fallar
con HTTP 503 según las variables
`MOCK_LATENCY_*` y `MOCK_FAILURE_RATE`; la aplicación reintenta la consulta al
iniciar.

## Respaldo y restauración

Ejecutar desde la raíz del repositorio y con los servicios iniciados.
Los scripts usan Bash:

```bash
bash scripts/backup.sh
bash scripts/restore.sh backups/AAAAMMDD-HHMMSS
```

El respaldo copia SQLite en caliente y detiene Keycloak brevemente para copiar
sus datos H2. Se conservan los últimos 14 respaldos. La restauración reemplaza
los datos actuales, solicita confirmación y vuelve a iniciar los servicios.
Los scripts se ejecutan manualmente; el repositorio no configura una tarea
programada. Para cumplir el RPO de dos días, quien administra el host debe
programar respaldos periódicos (ADR-08 y ADR-19).
Ambos scripts detectan los volúmenes montados por la instancia Compose de este
directorio, por lo que no dependen de que el proyecto se llame `red-barrial`.
También aceptan `docker compose` o `docker-compose`. Antes de ejecutarlos,
iniciá los servicios desde la raíz del repositorio.

## Estructura del repositorio

- `app/`: aplicación Django, configuración, autenticación, vistas y plantillas.
- `padron-mock/`: API FastAPI que simula el padrón provincial.
- `keycloak/realm/`: realm, cliente OIDC y roles importados por Keycloak.
- `keycloak-proxy/`: proxy que separa el acceso de usuarios de la consola
  administrativa.
- `scripts/`: respaldo y restauración de los datos.
- `docs/nfrs/nfr.md`: requisitos no funcionales objetivo.
- `docs/adr/`: índice de decisiones y ADRs disponibles.

El índice de [ADRs](docs/adr/README.md) contiene las decisiones documentadas,
incluidas las que precisan decisiones anteriores sin reemplazar sus archivos.
