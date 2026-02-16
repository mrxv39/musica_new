# workers/core/logging_utils.py

from __future__ import annotations

import time

from .detectors import mano_valida
from .types import TickCheck, WorkerPaths


def log_start(mesa: int, paths: WorkerPaths, x1: int, y1: int, x2: int, y2: int) -> None:
    print(f"[mesa {mesa}] worker START")
    print(f"[mesa {mesa}] root={paths.root}")
    print(f"[mesa {mesa}] db={paths.db_path}")
    print(f"[mesa {mesa}] main={paths.main_py}")
    print(f"[mesa {mesa}] roi=({x1},{y1})-({x2},{y2})")
    print("--------------------------------------------------")


def should_log(now_s: float, last_log_s: float, log_every_ms: int) -> bool:
    return (now_s - last_log_s) * 1000.0 >= log_every_ms


def print_tick(mesa: int, t: TickCheck) -> None:
    print(
        f"[mesa {mesa}] tick "
        f"cap={'OK' if t.cap_ok else 'FAIL'} "
        f"mano={t.mano or '(empty)'} valid={'Y' if mano_valida(t.mano) else 'N'} "
        f"time={'T' if t.time_ok else 'F'} "
        f"noboard={'T' if t.noboard_ok else 'F'} "
        f"img={t.img_path.name}"
    )

    if t.cap_err:
        print(f"[mesa {mesa}] {t.cap_err}")
    if t.mano_err:
        print(f"[mesa {mesa}] {t.mano_err}")
    if t.time_err:
        print(f"[mesa {mesa}] {t.time_err}")
    if t.noboard_err:
        print(f"[mesa {mesa}] {t.noboard_err}")
