# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\pipeline\dedupe.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DedupeState:
    last_sig: str = ""

    def is_duplicate(self, sig: str) -> bool:
        return sig == self.last_sig

    def update(self, sig: str) -> None:
        self.last_sig = sig
