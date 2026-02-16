# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\utils\time_utils.py

from __future__ import annotations

import time


def now_s() -> float:
    return time.time()


def dt_ms(t0: float, t1: float | None = None) -> int:
    if t1 is None:
        t1 = time.time()
    return int((t1 - t0) * 1000)
