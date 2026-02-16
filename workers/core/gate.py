# workers/core/gate.py

from __future__ import annotations

from .detectors import mano_valida
from .types import TickCheck


def gate_allows_pipeline(t: TickCheck) -> bool:
    # MISMA condición: cap_ok + mano válida + time y noboard en TRUE
    return t.cap_ok and mano_valida(t.mano) and (t.time_ok and t.noboard_ok)
