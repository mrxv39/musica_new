# workers/core/subprocess_utils.py

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple


def run_script(script_name: str, cwd: Path, image_path: Path) -> Tuple[int, str, str]:
    """
    Wrapper mínimo (MISMO comportamiento que un subprocess.run capture_output).
    Luego aquí meteremos timeout y stdout+stderr combinado sin tocar el resto del worker.
    """
    cmd = ["python", script_name, "--image", str(image_path)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    out = (r.stdout or "").strip()
    err = (r.stderr or "").strip()
    return r.returncode, out, err
