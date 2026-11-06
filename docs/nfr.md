# Requisitos no funcionales (NFR)

Dominio 1 · Banco de alimentos · Escenario 1A · Red barrial. NFR estrella: **simplicidad de operación y bajo costo**.

| ID | Atributo | Escenario medible | Prioridad |
|---|---|---|---|
| NFR-01 | Simplicidad de operación (estrella) | Un voluntario con conocimientos básicos despliega o reinicia el sistema con un único comando. | Muy alta |
| NFR-02 | Bajo costo | Costo de infraestructura ≤ USD 5–10/mes (o $0 en la PC donada); sin licencias; todo el stack open source. | Muy alta |
| NFR-03 | Trazabilidad y auditabilidad | Ante un reclamo, el coordinador obtiene el historial completo de un lote (ingreso, entregas, comedor, fecha, usuario). Ningún movimiento se borra ni se modifica. | Muy alta |
| NFR-04 | Mantenibilidad / modificabilidad | Un solo lenguaje y pocas dependencias. Las reglas de negocio (stock, vencimientos) están aisladas y cubiertas por tests. | Muy alta |
| NFR-05 | Tolerancia a fallos del padrón | Si el padrón no responde en 5 s, el sistema no se bloquea. Aplica una política definida (ver ADR-04) y deja constancia de la acción. | Alta |
| NFR-06 | Recuperabilidad | RPO ≤ 2 días (se pierde como máximo dos días de datos) y RTO ≤ 4 h. | Alta |
| NFR-07 | Integridad de datos | El stock por lote nunca es negativo; una entrega descuenta stock de forma atómica (todo o nada), incluso ante fallos a mitad de operación. | Alta |
| NFR-08 | Seguridad | Autenticación obligatoria; permisos por rol (depósito, referente, coordinador); contraseñas con hash; acceso limitado a la red local. | Media |
| NFR-09 | Disponibilidad | Disponible en el horario operativo del depósito. No se requiere 24/7 ni alta disponibilidad. | Media |

## NFRs descartados

Usabilidad, observabilidad, portabilidad, rendimiento y escalabilidad. No condicionan el diseño.
HTTPS tampoco es necesario: el sistema es local, dockerizado y sin salida al exterior.

## Matriz NFR ↔ ADR

| ADR | NFR que lo justifican |
|---|---|
| ADR-01 Monolito modular | 01, 02, 04, 09 |
| ADR-02 SQLite en modo WAL | 01, 02, 06, 07 |
| ADR-03 Ledger append-only con FEFO | 03, 07 |
| ADR-04 Padrón: adaptador, timeout y caché | 03, 05 |
| ADR-05 UI renderizada en servidor | 01, 02, 04 |
| ADR-06 Python + Django | 02, 04 |
| ADR-07 Docker Compose | 01, 09 |
| ADR-08 Backup y recuperación | 01, 06 |
| ADR-09 OIDC con Keycloak | 08 (tensiona 01 y 02) |
| ADR-10 Auditoría | 03 |
| ADR-11 Confirmación por estados e idempotencia | 03, 07 |
| ADR-12 padron-mock | 04, 05 |
| ADR-13 Reglas de negocio en servicios con tests | 04, 07 |
| ADR-14 Restricción de la consola de administración de Keycloak | 08 (tensiona 01 y 02) |
