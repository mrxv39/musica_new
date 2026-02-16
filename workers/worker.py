# C:\Users\Usuario\Desktop\projectos\musica_new\workers\worker.py
# Wrapper robusto: asegura sys.path correcto + preflight rápido de imports

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_project_root_on_syspath() -> Path:
    """
    Cuando ejecutas: python workers\\worker.py
    el cwd y sys.path pueden no incluir la raíz del proyecto.
    Forzamos añadirla para que 'import workers.core...' funcione.
    """
    this_file = Path(__file__).resolve()
    project_root = this_file.parents[1]  # .../musica_new
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    return project_root


def _preflight_imports() -> None:
    """
    Falla rápido con un error claro si hay problemas de packaging/import.
    """
    try:
        from workers.core.cli import main as _main  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "Preflight import failed: no puedo importar 'workers.core.cli'.\n"
            "Causas típicas:\n"
            "- Falta workers/__init__.py\n"
            "- Falta workers/core/__init__.py\n"
            "- Estás ejecutando desde otra carpeta (aunque este wrapper ya añade project_root a sys.path)\n"
            f"Detalle: {e!r}"
        ) from e


def main() -> int:
    _ensure_project_root_on_syspath()
    _preflight_imports()

    from workers.core.cli import main as core_main
    return core_main()


if __name__ == "__main__":
    raise SystemExit(main())
