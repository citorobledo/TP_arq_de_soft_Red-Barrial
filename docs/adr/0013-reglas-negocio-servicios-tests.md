# ADR-13: Reglas de negocio en servicios con tests

- **Estado:** Propuesto
- **Fecha:** 2026-11-01
- **NFR:** 04, 07

## Contexto
NFR-04 exige reglas de negocio aisladas y cubiertas por tests.

## Decisión
Cada módulo concentra sus reglas en `services.py`, sin depender de vistas, plantillas ni HTTP; las vistas son delgadas. Tests automáticos con el runner de Django que cubren, como mínimo:
- el stock por lote nunca es negativo;
- la entrega es atómica (todo o nada);
- la selección FEFO;
- los movimientos no se modifican;
- el comportamiento con el padrón caído;
- el mapeo de roles.

Ejecución: `docker compose run --rm app python manage.py test`.

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Lógica en vistas y modelos | Menos archivos | Difícil de probar y de cambiar |
| pytest | Sintaxis más cómoda | Dependencia adicional |

## Consecuencias
- Las reglas se prueban sin levantar el sistema completo.
- Requiere disciplina para no mezclar reglas en las vistas.
