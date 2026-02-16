# workers/core/detectors.py

from __future__ import annotations

import re
from pathlib import Path
from typing import Tuple

from .subprocess_utils import run_script

VALID_HAND_REGEX = re.compile(r"^[2-9TJQKA][cdhs][2-9TJQKA][cdhs]$")


def mano_valida(mano: str) -> bool:
    if not mano or mano == "NN":
        return False
    return bool(VALID_HAND_REGEX.match(mano))


def detectar_mano(root: Path, image_path: Path) -> tuple[str, str]:
    """
    Mantiene la lógica base: si hay stderr -> se reporta como error y mano vacía.
    Busca 'MANO = XXxx' en stdout.
    """
    rc, out, err = run_script("reconocer_mano.py", cwd=root, image_path=image_path)

    if err:
        return "", f"[reconocer_mano.py stderr] {err}"

    m = re.search(r"MANO\s*=\s*([2-9TJQKA][cdhs][2-9TJQKA][cdhs])", out)
    return (m.group(1) if m else ""), ""


def detectar_time(root: Path, image_path: Path) -> tuple[bool, str]:
    rc, out, err = run_script("encontrar_time.py", cwd=root, image_path=image_path)

    if err:
        return False, f"[encontrar_time.py stderr] {err}"

    return ("TRUE" in out.upper()), ""


def detectar_noboard(root: Path, image_path: Path) -> tuple[bool, str]:
    rc, out, err = run_script("encontrar_noboard.py", cwd=root, image_path=image_path)

    if err:
        return False, f"[encontrar_noboard.py stderr] {err}"

    return ("TRUE" in out.upper()), ""
