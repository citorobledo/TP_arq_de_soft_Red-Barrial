# Red barrial · Banco de alimentos

Trabajo práctico de Arquitectura de Software 1. Prototipo local para una red
barrial de comedores.

> **Estado del proyecto:** la base web y la autenticación están implementadas,
> pero todavía no están desarrolladas las funciones de negocio para registrar
> donaciones, lotes o entregas. El padrón disponible es un servicio simulado y
> aún no está integrado con la aplicación.

## Funcionalidad disponible

- Inicio web y panel autenticado, implementados con Django y plantillas del
  servidor.
- Inicio y cierre de sesión delegados a Keycloak mediante OpenID Connect
  (OIDC).
- Sincronización de los roles de Keycloak con grupos de Django. Los roles
  configurados son `voluntario_deposito`, `referente_comedor` y `coordinador`.
- API simulada del padrón provincial, con demoras y errores configurables.
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
| Identidad | Keycloak 26 por OIDC; un proxy Nginx bloquea la consola administrativa en el puerto de login. |
| Persistencia | SQLite en modo WAL para Django; H2 en archivo para Keycloak. Ambos datos viven en volúmenes Docker. |
| Padrón simulado | FastAPI y Uvicorn; expone endpoints REST con demoras y fallas configurables. |
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

La aplicación ejecuta las migraciones y recopila los archivos estáticos al
iniciar. Para detener los servicios:

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
| Retorno OIDC | http://localhost:8000/oidc/callback/ | URL de retorno de Keycloak; no abrir manualmente |
| Cierre de sesión OIDC | http://localhost:8000/oidc/logout/ | Se envía mediante el formulario de cierre de sesión de la aplicación |
| Consola de administración de Keycloak | http://localhost:8081/admin/ | Sólo accesible desde la computadora que ejecuta Docker; credenciales de administrador de `.env` |
| Cuenta del realm en Keycloak | http://localhost:8080/realms/red-barrial/account/ | Acceso a la cuenta del usuario del realm |
| Configuración OIDC del realm | http://localhost:8080/realms/red-barrial/.well-known/openid-configuration | Documento JSON para comprobar que el realm responde |
| Swagger UI del padrón simulado | http://localhost:8001/docs | Sólo accesible desde la computadora que ejecuta Docker |
| Redoc del padrón simulado | http://localhost:8001/redoc | Sólo accesible desde la computadora que ejecuta Docker |
| Salud del padrón simulado | http://localhost:8001/health | Responde `{"status":"ok"}` |
| Lista de comedores de prueba | http://localhost:8001/comedores | API de ejemplo; puede demorar o responder HTTP 503 |
| Consulta de comedor de prueba | http://localhost:8001/comedores/CP-001 | API de ejemplo; puede demorar o responder HTTP 503 |

El realm `red-barrial` y el cliente OIDC `red-barrial-web` se importan al
iniciar Keycloak. No se crean usuarios automáticamente: hay que dar de alta
las cuentas y asignarles los roles del realm desde la consola administrativa.
Al iniciar sesión, el panel muestra el usuario y sus roles; todavía no hay
pantallas de negocio con permisos por rol.

Para comprobar el flujo principal, abrir `/`, iniciar sesión desde el botón
**Ingresar con Keycloak** y verificar que se vuelve al panel en `/panel/`.
Asignar previamente un rol al usuario desde la consola de administración para
verlo reflejado en el panel. El padrón es un servicio independiente: sus
endpoints permiten probar el mock, pero todavía no están conectados a la
aplicación.

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

## Variables de entorno

| Variable | Uso |
|---|---|
| `PUBLIC_HOST` | Host público de la aplicación en la red local; por defecto, `localhost`. |
| `KEYCLOAK_VERSION` | Versión de la imagen de Keycloak; por defecto, `26.0`. |
| `KEYCLOAK_ADMIN`, `KEYCLOAK_ADMIN_PASSWORD` | Usuario y contraseña iniciales del administrador de Keycloak. |
| `OIDC_CLIENT_SECRET` | Secreto del cliente OIDC; debe coincidir entre la configuración de Keycloak y Django. |
| `DJANGO_SECRET_KEY` | Clave secreta de Django. |
| `MOCK_LATENCY_MIN`, `MOCK_LATENCY_MAX` | Demora mínima y máxima del padrón simulado, en segundos. |
| `MOCK_FAILURE_RATE` | Probabilidad de error del padrón, entre `0` y `1`. |

No publicar el archivo `.env` ni reutilizar sus secretos en otros entornos. La
configuración usa HTTP, Keycloak en modo de desarrollo y almacenamiento H2:
está pensada para el prototipo en una red local, no para exponer el sistema a
Internet o usarlo en producción.

## Padrón provincial simulado

El servicio `padron-mock` ofrece:

- `GET /health`: estado del servicio, sin demora aleatoria.
- `GET /comedores`: lista de comedores de ejemplo.
- `GET /comedores/{codigo}`: consulta un comedor por código.

Las consultas al padrón pueden demorarse y fallar con HTTP 503 según las
variables `MOCK_LATENCY_*` y `MOCK_FAILURE_RATE`. Los códigos y datos son
estáticos y ficticios. La aplicación Django aún no consume estos endpoints.

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
- `docs/nfr.md`: requisitos no funcionales objetivo.
- `docs/adr/`: índice de decisiones y ADRs disponibles.

El índice de ADRs incluye decisiones planificadas que todavía no están
presentes como archivos. En el repositorio actual están los ADR-07, ADR-09 y
ADR-14, además de la plantilla.
