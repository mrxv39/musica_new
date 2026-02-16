# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\pipeline\tick_state.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from workers.core.types import TickCheck


@dataclass
class TickState:
    last_key: str = ""

    def changed(self, tick: TickCheck) -> bool:
        key = self._key(tick)
        if key == self.last_key:
            return False
        self.last_key = key
        return True

    @staticmethod
    def _key(tick: TickCheck) -> str:
        # Solo lo que importa para el usuario en consola
        cap = "OK" if tick.cap_ok else "FAIL"
        mano = tick.mano or "(empty)"
        t = "T" if tick.time_ok else "F"
        nb = "T" if tick.noboard_ok else "F"
        return f"{cap}|{mano}|{t}|{nb}"
