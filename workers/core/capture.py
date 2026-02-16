# workers/core/capture.py

from __future__ import annotations

from pathlib import Path
from PIL import ImageGrab


def capture_region(x1: int, y1: int, x2: int, y2: int, out_path: Path) -> None:
    img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(out_path), format="BMP")

