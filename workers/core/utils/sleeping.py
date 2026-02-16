# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\utils\sleeping.py

from __future__ import annotations

import time


def sleep_ms(ms: int) -> None:
    time.sleep(max(ms, 0) / 1000.0)


def sleep_short() -> None:
    # “poll” suave cuando el gate no se cumple
    time.sleep(0.3)


def sleep_interval(interval_ms: int) -> None:
    # ritmo del worker (nunca menos de 300ms)
    time.sleep(max(interval_ms, 300) / 1000.0)
