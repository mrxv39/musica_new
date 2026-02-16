# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\pipeline\tick_logging.py

from __future__ import annotations

from workers.core.gate import gate_allows_pipeline
from workers.core.logging_utils import print_tick
from workers.core.types import TickCheck

from .tick_state import TickState


def maybe_log_tick(
    mesa: int,
    tick: TickCheck,
    busy: bool,
    tick_state: TickState,
) -> None:
    """
    Reglas:
    - Nunca loguear si busy
    - Nunca loguear si gate TRUE (no ensuciar alrededor del pipeline)
    - Loguear SOLO si cambia el estado (cap/mano/time/noboard)
    """
    if busy:
        return

    if gate_allows_pipeline(tick):
        return

    if tick_state.changed(tick):
        print_tick(mesa, tick)
