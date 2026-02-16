# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\pipeline\cooldown.py

from __future__ import annotations

from dataclasses import dataclass

from workers.core.utils.time_utils import now_s


@dataclass
class Cooldown:
    until_s: float = 0.0
    _logged: bool = False

    def active(self, now: float | None = None) -> bool:
        if now is None:
            now = now_s()
        return now < self.until_s

    def start_ms(self, ms: int) -> None:
        self.until_s = now_s() + (max(ms, 0) / 1000.0)
        self._logged = False

    def remaining_ms(self, now: float | None = None) -> int:
        if now is None:
            now = now_s()
        return max(0, int((self.until_s - now) * 1000))

    def should_log_once(self) -> bool:
        if self._logged:
            return False
        self._logged = True
        return True
