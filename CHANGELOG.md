# Changelog

Todos los cambios relevantes del proyecto se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
versionado sigue [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

## [1.0.0] - 2026-11-19

Primera versión estable: entrega final del trabajo práctico.

### Added
- Modelo de datos (8 migraciones): productos y lotes, comedores, entregas y detalles de entrega. El stock no negativo está garantizado por una restricción de la base de datos.
- Capa de servicios y repositorios con tipos inmutables (ADR-15) y vistas organizadas por módulo (ADR-16).
- Pantallas por rol: depósito (ingreso de lotes con fecha de ingreso y donante, nueva entrega y mensajes de confirmación), comedor (recepción de entregas por el referente) y coordinador (reportes y exportación CSV). El voluntario de una entrega es el usuario con sesión iniciada; no se pueden seleccionar comedores no habilitados.
- API REST con documentación OpenAPI (Django Ninja) y errores con formato Problem Details. Exige sesión de Keycloak y rol de depósito o coordinador; un test recorre todas las operaciones del esquema y verifica que ninguna responde sin sesión.
- Sincronización de los comedores con el padrón provincial al iniciar la aplicación y servicio simulado `padron-mock` (ADR-04 y ADR-12).
- Acceso remoto opcional con un túnel ngrok (perfil `publico` de Compose, imagen fijada en 3.39.0) y lista de rutas permitidas en el proxy (ADR-17).
- Servicio `keycloak-admin-realm-config` y bloqueo del realm `master` en los puertos 8080 y 8090: la autenticación de administración queda solo en `127.0.0.1:8081` (ADR-20).
- Usuarios de prueba por rol (voluntario, referente y coordinador) en el realm de Keycloak.
- Documentación: ADR-01 a ADR-21 (los ADR-18 a ADR-21 precisan lo vigente sin reemplazar los anteriores), verificación de NFRs en `docs/nfrs/verificacion-nfrs.md` y documento de arquitectura.
- 48 tests, que incluyen pruebas de arquitectura para ADR-01 y ADR-15.
- Este changelog.

### Changed
- Se retira la vista `panel`; los accesos pasan a las pantallas por rol.
- La API REST ya no acepta `estado`, `fecha_confirmacion` ni `nombre_voluntario` del cliente: el voluntario sale de la sesión y toda entrega nueva queda "registrada".
- Los finales de línea se normalizan a LF (`.gitattributes`): los scripts de respaldo y restauración vuelven a ser ejecutables en Linux.

### Security
- `.env.example` usa marcadores (`cambiar-esto`). Los secretos que estuvieron publicados en el historial (contraseña de administrador de Keycloak, secreto del cliente OIDC y clave de Django) deben rotarse.

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

[Sin publicar]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/citorobledo/TP_arq_de_soft_Red-Barrial/releases/tag/v0.1.0
