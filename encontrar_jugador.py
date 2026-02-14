# encontrar_jugador.py
# Dado un nombre (p2name/p3name), devuelve su "tipo" desde DB.
# Si no existe, lo crea como fish.
# Sin prints. Tipos puros.

from __future__ import annotations

from typing import Tuple

from players_repo import get_or_create_player_tipo, DEFAULT_SALA


def run_quiet(p2name: str, p3name: str, sala: str = DEFAULT_SALA) -> Tuple[str, str]:
    p2tipo = get_or_create_player_tipo(p2name, sala=sala) if p2name else "fish"
    p3tipo = get_or_create_player_tipo(p3name, sala=sala) if p3name else "fish"
    return p2tipo, p3tipo


if __name__ == "__main__":
    # test manual rápido
    p2, p3 = run_quiet("troybomber", "Dilligaff")
    print("p2tipo:", p2)
    print("p3tipo:", p3)
