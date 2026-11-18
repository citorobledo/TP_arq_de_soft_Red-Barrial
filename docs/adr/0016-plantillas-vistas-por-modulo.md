# ADR-16: Ubicación de vistas y plantillas HTML dentro de cada módulo (Vertical Slice)

- **Estado:** Aceptado
- **Fecha:** 2026-11-15
- **NFR:** 01, 04

## Contexto
Con la incorporación de las vistas y plantillas HTML de la aplicación, los primeros prototipos de interfaz (`deposito.html`, `coordinador.html`) y sus vistas habían quedado alojados dentro del módulo `seguridad`. Esto rompe la cohesión modular definida en ADR-01 (monolito modular), ya que `seguridad` debe encargarse únicamente de la autenticación (OIDC) y del control de acceso por roles, sin contener vistas ni plantillas de depósito o reportes. Asimismo, el motor de plantillas de Django ya tiene habilitado `APP_DIRS=True` en `settings.py`, lo que permite descubrir plantillas dentro de cada aplicación de `apps/`.

## Decisión
Organizar las vistas (`views.py`, `urls.py`) y plantillas HTML (`templates/<modulo>/`) dentro de cada módulo de dominio correspondiente (enfoque *Vertical Slice*):
1. El módulo `seguridad` conserva únicamente sus vistas y plantillas propias (`home.html`, `panel.html`, `sin_permisos.html` en `apps/seguridad/templates/seguridad/`).
2. La vista y plantilla del panel de depósito se ubican en el módulo `deposito` (`apps/deposito/views.py`, `apps/deposito/urls.py` y `apps/deposito/templates/deposito/deposito.html`).
3. Las vistas y plantillas transversales de coordinación y exportación CSV se ubican en un módulo dedicado `reportes` (`apps/reportes/views.py`, `apps/reportes/urls.py` y `apps/reportes/templates/reportes/coordinador.html`), tal como prevé ADR-01.
4. La carpeta global `app/src/templates/` queda reservada exclusivamente para la plantilla base compartida (`base.html`).

## Alternativas consideradas
| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Centralizar todas las plantillas en `app/src/templates/<modulo>/` | Un único directorio raíz para editar archivos HTML | Divide cada módulo entre `apps/` (código Python) y `templates/` (HTML), reduciendo la encapsulación por módulo |
| Mantener todas las vistas y plantillas dentro de `seguridad` | Cero movimientos de archivos iniciales | Viola ADR-01 y mezcla responsabilidades de autenticación con inventario y reportes |

## Consecuencias
- Cada módulo es autocontenido de extremo a extremo (*vertical slice*: `models.py`, `repositories.py`, `services.py`, `api.py`, `views.py`, `urls.py` y `templates/<modulo>/`), mejorando la mantenibilidad y las fronteras del monolito modular (NFR-04).
- No requiere cambios de infraestructura ni complejidad operativa adicional (NFR-01), ya que Django descubre las plantillas automáticamente mediante `APP_DIRS=True`.
- Como contrapartida aceptada, al editar interfaces HTML en varios módulos se debe navegar entre las subcarpetas `apps/<modulo>/templates/`, y las páginas transversales se centralizan en `apps/reportes/`.
