"""Pruebas arquitectónicas (Fitness Functions) basadas en AST para ADR-01 y ADR-15."""

import ast
from pathlib import Path

from django.test import SimpleTestCase

APPS_DIR = Path(__file__).resolve().parent
SRC_DIR = APPS_DIR.parent


def _iterar_modulos() -> list[Path]:
    return sorted(
        p
        for p in APPS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    )


def _iterar_archivos_modulo(modulo_dir: Path) -> list[Path]:
    archivos = []
    for archivo in sorted(modulo_dir.rglob("*.py")):
        partes_rel = archivo.relative_to(modulo_dir).parts
        if "migrations" in partes_rel or "__pycache__" in partes_rel:
            continue
        if archivo.name == "tests.py":
            continue
        archivos.append(archivo)
    return archivos


def _obtener_imports(archivo: Path) -> set[str]:
    """Extrae todos los módulos/símbolos importados (incluidos relativos) usando AST."""
    arbol = ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))
    partes_paquete = archivo.relative_to(SRC_DIR).parent.parts
    imports: set[str] = set()

    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                imports.add(alias.name)
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level > 0:
                subida = nodo.level - 1
                base_parts = partes_paquete[: len(partes_paquete) - subida]
                base = (
                    ".".join((*base_parts, nodo.module))
                    if nodo.module
                    else ".".join(base_parts)
                )
            else:
                base = nodo.module or ""

            if base:
                imports.add(base)
                for alias in nodo.names:
                    if alias.name != "*":
                        imports.add(f"{base}.{alias.name}")

    return imports


def _es_capa_app(imp: str, capas: tuple[str, ...]) -> bool:
    partes = imp.split(".")
    return len(partes) >= 3 and partes[0] == "apps" and partes[2] in capas


class ArquitecturaTests(SimpleTestCase):
    """Verifica las reglas de monolito modular (ADR-01) y capas limpias (ADR-15)."""

    def test_vistas_y_api_no_importan_modelos_ni_repositorios(self):
        """ADR-15: views.py y api.py solo consumen services/dtos, nunca models ni repositories."""
        for modulo_dir in _iterar_modulos():
            for capa in ("views.py", "api.py"):
                archivo = modulo_dir / capa
                if not archivo.exists():
                    continue
                prohibidos = sorted(
                    imp
                    for imp in _obtener_imports(archivo)
                    if _es_capa_app(imp, ("models", "repositories"))
                )
                self.assertEqual(
                    prohibidos,
                    [],
                    f"{modulo_dir.name}/{capa} viola ADR-15 al importar: {prohibidos}",
                )

    def test_servicios_y_repositorios_no_importan_vistas_ni_api(self):
        """ADR-15: services.py y repositories.py no dependen de HTTP ni de capas de entrega."""
        for modulo_dir in _iterar_modulos():
            for capa in ("services.py", "repositories.py"):
                archivo = modulo_dir / capa
                if not archivo.exists():
                    continue
                prohibidos = sorted(
                    imp
                    for imp in _obtener_imports(archivo)
                    if _es_capa_app(imp, ("views", "api", "urls"))
                )
                self.assertEqual(
                    prohibidos,
                    [],
                    f"{modulo_dir.name}/{capa} viola ADR-15 al importar: {prohibidos}",
                )

    def test_modulos_no_importan_modelos_ni_repositorios_ajenos(self):
        """ADR-01 y ADR-15: cada módulo solo interactúa con otros a través de `services`."""
        for modulo_dir in _iterar_modulos():
            for archivo in _iterar_archivos_modulo(modulo_dir):
                prohibidos = sorted(
                    imp
                    for imp in _obtener_imports(archivo)
                    if _es_capa_app(imp, ("models", "repositories"))
                    and imp.split(".")[1] != modulo_dir.name
                )
                self.assertEqual(
                    prohibidos,
                    [],
                    f"{modulo_dir.name}/{archivo.name} accede a capa interna ajena: {prohibidos}",
                )

    def test_dependencias_unidireccionales_entre_modulos(self):
        """ADR-01: el grafo de dependencias entre módulos fluye sin ciclos."""
        prohibiciones = {
            "seguridad": {"deposito", "comedores", "entregas", "reportes"},
            "deposito": {"comedores", "entregas", "reportes"},
            "comedores": {"reportes"},
            "entregas": {"reportes"},
        }
        for modulo, no_permitidos in prohibiciones.items():
            modulo_dir = APPS_DIR / modulo
            for archivo in _iterar_archivos_modulo(modulo_dir):
                for imp in _obtener_imports(archivo):
                    partes = imp.split(".")
                    if len(partes) >= 2 and partes[0] == "apps" and partes[1] in no_permitidos:
                        self.fail(
                            f"Violación ADR-01: {modulo}/{archivo.name} importa {imp}"
                        )

        servicios_comedores = APPS_DIR / "comedores" / "services.py"
        for imp in _obtener_imports(servicios_comedores):
            self.assertFalse(
                imp.startswith("apps.entregas"),
                f"Violación ADR-01: comedores/services.py importa {imp}",
            )
