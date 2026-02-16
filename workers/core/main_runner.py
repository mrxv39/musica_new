# workers/core/main_runner.py

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Tuple


def run_main_json(main_py: Path, image_path: Path, cwd: Path) -> tuple[dict | None, str]:
    cmd = ["python", str(main_py), "--image", str(image_path), "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))

    if r.returncode != 0:
        return None, f"[main stderr]\n{(r.stderr or '').strip()}"

    raw = (r.stdout or "").strip()
    try:
        return json.loads(raw), ""
    except Exception:
        return None, f"[worker] Error parsing JSON from main. stdout was:\n{raw}"
