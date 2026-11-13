# ADR-15: Separación en capas de servicios y repositorios sobre el ORM (Clean Architecture)

- **Estado:** Aceptado
- **Fecha:** 2026-11-02
- **NFR:** 04, 07

## Contexto
Para cumplir con la mantenibilidad y modificabilidad del sistema (NFR-04) y preservar la integridad de datos en las operaciones de inventario y entregas (NFR-07), las reglas de negocio deben permanecer desacopladas tanto de la interfaz web (`views.py`, plantillas o futuros endpoints HTTP) como de las consultas directas del ORM de Django sobre SQLite. Asimismo, según ADR-01 y ADR-13, cada módulo del dominio (`productos`, `deposito`, `comedores`, `entregas`) debe mantener sus responsabilidades aisladas y comunicarse en un único sentido sin modificar directamente los modelos internos de otros módulos.

## Decisión
Adoptar una separación en capas inspirada en *Clean Architecture* dentro de cada módulo (`apps/<modulo>/`), dividiendo la lógica en:
1. **Capa de Casos de Uso / Servicios (`services.py`):** concentra las reglas de negocio, validaciones de dominio, transiciones de estado (`registrada` → `confirmada` / `anulada`) y atomicidad (`@transaction.atomic`), sin ejecutar consultas directas del ORM ni depender de HTTP.
2. **Capa de Acceso a Datos / Repositorios (`repositories.py`):** encapsula todas las operaciones CRUD del ORM de Django (`select_for_update`, `select_related`, `prefetch_related`, `full_clean`, `save`, `delete`) sobre `models.py`.
3. **Comunicación entre módulos por servicios:** un módulo consumidor (como `entregas`) no accede ni modifica directamente el modelo o repositorio de otro módulo (`Lote`), sino que invoca únicamente los casos de uso expuestos en `apps.deposito.services` (`descontar_stock`, `restituir_stock`).

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Consultas ORM mezcladas en `views.py` | Menos archivos inicialmente | Acopla las reglas de negocio al frontend/HTTP; dificulta las pruebas unitarias (contradice NFR-04 y ADR-13) |
| Consultas ORM directas en `services.py` sin `repositories.py` | Una capa menos por módulo | Mezcla reglas de dominio con detalles de persistencia y permite que un módulo manipule tablas ajenas directamente |
| Entidades de dominio puras + mapeadores manuales (DDD estricto) | Independencia total del framework | Sobrecarga de código repetitivo (*boilerplate*) desproporcionada para la escala del proyecto (tensiona NFR-01 y NFR-04) |

## Consecuencias
- Las futuras vistas (`GET`, `POST`, `PUT`, `DELETE`) serán delgadas y solo invocarán funciones de `services.py`, siendo independientes de si la respuesta se renderiza en HTML o se devuelve en JSON.
- La integridad del stock (NFR-07) queda centralizada en `apps.deposito.services`, evitando descuentos o restituciones inconsistentes desde otros módulos.
- Las consultas y bloqueos de fila (`select_for_update`) sobre SQLite quedan concentrados en `repositories.py`, facilitando el mantenimiento y las pruebas automatizadas (NFR-04).
- Agrega un archivo adicional (`repositories.py`) por cada módulo de negocio, costo aceptable frente a la claridad de fronteras obtenida.
