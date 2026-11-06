# ADR-01: Monolito modular

- **Estado:** Aceptado
- **Fecha:** 2026-11-01
- **NFR:** 01, 02, 04, 09

## Contexto
Un depósito, 8 comedores y unos 300 movimientos por mes. Lo mantiene un voluntario con conocimientos básicos de programación, unas pocas horas por semana. No se requiere alta disponibilidad (NFR-09).

## Decisión
Una única aplicación desplegable, organizada en módulos por carpeta: `seguridad`, `catalogo`, `inventario`, `entregas`, `reportes`, `padron` y `auditoria`. Las dependencias van en un solo sentido (`entregas` usa `inventario`, nunca al revés).

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Microservicios | Despliegue y escalado independientes | Más piezas que operar y diagnosticar; contradice NFR-01 y 02 |
| Monolito sin módulos | Aún más simple al inicio | Reglas mezcladas; dificulta NFR-04 |

## Consecuencias
- Un solo proceso y un solo despliegue.
- Si la aplicación cae, cae todo el sistema; se acepta por NFR-09.
- No hay escalado independiente por módulo (escalabilidad descartada).
- El orden de dependencias entre módulos se mantiene por disciplina y revisión de código.
