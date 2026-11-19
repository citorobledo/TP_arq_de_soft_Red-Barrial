# ADR-21: Cobertura actual de pruebas de reglas de negocio

- **Estado:** Aceptado
- **Fecha:** 2026-11-18
- **NFR:** 04, 07
- **Actualiza:** precisa el alcance verificable de pruebas de ADR-13 sin reemplazar su archivo.

## Contexto
ADR-13 enumera casos mínimos de prueba para las reglas de negocio. La suite actual usa el runner de Django y contiene 48 métodos `test_` en cinco archivos. La cobertura implementada es parcial respecto de esa lista, por lo que la existencia de pruebas no debe interpretarse como cumplimiento de todos los casos propuestos.

## Decisión
- Se considera implementada y cubierta la creación de lotes con stock no negativo, el rechazo de descuentos inválidos o superiores al stock disponible y la atomicidad de una entrega cuando falla uno de sus detalles.
- FEFO está probado como ordenamiento y filtrado de la lista de lotes; no hay una prueba de asignación automática de stock a una entrega por FEFO.
- Los permisos de la API están probados para usuarios sin sesión, referentes, depósito, coordinadores y usuarios sin rol. También se prueban CSRF y algunos campos protegidos. No se prueba la extracción de roles del token OIDC ni su sincronización a grupos de Django.
- La sincronización exitosa del padrón está probada para códigos coincidentes, sin coincidencia y sin cambios, verificando que solo se actualice `habilitado`. No hay pruebas de error del padrón, reintentos ni agotamiento de intentos.
- No se considera probado ni implementado el carácter inmutable o append-only de los movimientos: los tests actuales ejercitan la actualización y eliminación de entregas/detalles y la restitución de stock.
- Para ejecutar la suite sin inicializar la aplicación sobre su volumen de datos: `docker compose run --rm --no-deps --entrypoint python app manage.py test`. El `entrypoint.sh` normal ejecuta migraciones, sincroniza el padrón y recopila estáticos antes del comando; las pruebas no necesitan esos pasos ni los servicios externos.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Mantener la lista de ADR-13 como cobertura lograda | No requiere cambios documentales | Afirma cobertura que la suite actual no verifica |
| Registrar cobertura real y brechas pendientes | Distingue comportamiento verificado de objetivos pendientes | La suite no cubre todavía todos los casos de ADR-13 |

## Consecuencias
- ADR-13 sigue definiendo objetivos de prueba; este ADR documenta qué parte de ellos está efectivamente cubierta hoy.
- Las brechas sobre fallos del padrón, mapeo de roles, selección FEFO e inmutabilidad deben cerrarse con cambios de comportamiento y/o pruebas antes de afirmar cumplimiento completo de ADR-13.
- La suite incluye además pruebas de CRUD y fitness functions arquitectónicas para ADR-01 y ADR-15, que no sustituyen los casos de negocio faltantes.

## Evidencia en el proyecto
- `app/src/apps/deposito/tests.py`: stock, orden FEFO y lotes por vencer.
- `app/src/apps/entregas/tests.py`: atomicidad, transiciones, confirmación idempotente y edición/eliminación de detalles.
- `app/src/apps/comedores/tests.py`: sincronización exitosa del padrón y validaciones de comedores.
- `app/src/apps/seguridad/tests.py`: autorización de API por sesión y rol; no prueba el backend OIDC.
- `app/src/apps/tests.py`: reglas arquitectónicas de ADR-01 y ADR-15.
- `app/src/apps/seguridad/backends.py`: extracción y sincronización de roles OIDC sin pruebas dedicadas en la suite actual.
