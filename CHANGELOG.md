# Changelog

Todos los cambios relevantes del proyecto se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
versionado sigue [SemVer](https://semver.org/lang/es/) (`0.y.z` = desarrollo inicial).

## [Sin publicar]

<!-- Antes de publicar v0.3.0: tests en rojo (8 en dev) y normalización de finales de línea. -->

### Added
- Modelos y migraciones del dominio: productos y lotes, comedores, entregas y detalles de entrega.
- Capa de servicios y repositorios con tipos inmutables (ADR-15) y vistas organizadas por módulo (ADR-16).
- Pantalla del depósito: ingreso de lotes (con fecha de ingreso y donante), formulario de nueva entrega y mensajes de confirmación. El voluntario de la entrega es el usuario con sesión iniciada y no se puede cambiar; no se pueden seleccionar comedores no habilitados.
- Pantalla del comedor: recepción de entregas por el referente.
- Panel del coordinador con reportes.
- API REST con documentación OpenAPI (Django Ninja) y errores con formato Problem Details.
- Sincronización de los comedores con el padrón provincial al iniciar la aplicación.
- 33 tests unitarios (CRUD y referente de comedor).
- Acceso remoto opcional con un túnel ngrok (perfil `publico` de Compose) y lista de rutas permitidas en el proxy (ADR-17).
- Autenticación de la API REST: exige sesión de Keycloak y rol de depósito o coordinador, con tests que verifican que toda operación lo exige.

### Changed
- Se retira la vista `panel`; los accesos pasan a las pantallas por rol.
- La API REST ya no acepta `estado`, `fecha_confirmacion` ni `nombre_voluntario` del cliente: el voluntario sale de la sesión y toda entrega nueva queda "registrada".

### Security
- `.env.example` vuelve a usar marcadores (`cambiar-esto`). Los secretos que estuvieron publicados (contraseña de administrador de Keycloak, secreto del cliente OIDC y clave de Django) deben rotarse.

## [0.2.0] - 2026-11-17

### Added
- Panel del voluntario de depósito (`/deposito/`) protegido por rol, con estilos y logo.
- Pantallas de inicio con accesos según el rol.

## [0.1.1] - 2026-11-15

### Fixed
- Limpieza de archivos duplicados de la raíz y de metadatos de Windows (`Zone.Identifier`).
- Correcciones mínimas.

## [0.1.0] - 2026-11-15

### Added
- Entorno con Docker Compose: aplicación Django, Keycloak y `padron-mock` (padrón provincial simulado).
- Login con Keycloak (OIDC) y roles del dominio (voluntario de depósito, referente de comedor, coordinador).
- Proxy nginx que restringe la consola de administración de Keycloak al servidor (ADR-14).
- Healthchecks de los servicios y scripts de respaldo y restauración.
- Documentación: requisitos no funcionales y ADR-01 a ADR-14.

[Sin publicar]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/releases/tag/v0.1.0
