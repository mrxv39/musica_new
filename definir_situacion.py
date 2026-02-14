# definir_situacion.py
# Deriva "situación" de preflop a partir del dict del pipeline (dealer, stacks, etc.)
# Convención: hero = p1
# Sin prints. Devuelve tipos puros.

from __future__ import annotations

from typing import Dict, Any, Tuple, List


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _positions_3max(dealer: str) -> Dict[str, str]:
    # dealer indica BTN
    d = (dealer or "").strip().lower()
    if d == "p1":
        return {"p1": "BTN", "p2": "SB", "p3": "BB"}
    if d == "p2":
        return {"p2": "BTN", "p3": "SB", "p1": "BB"}
    if d == "p3":
        return {"p3": "BTN", "p1": "SB", "p2": "BB"}
    return {"p1": "UNK", "p2": "UNK", "p3": "UNK"}


def _active_players(stacks: Dict[str, float]) -> List[str]:
    # activo si stack > 0.1
    act = []
    for p in ("p1", "p2", "p3"):
        if stacks.get(p, 0.0) > 0.1:
            act.append(p)
    return act


def _normalize_sit(hero_pos: str, vill_positions: List[str]) -> str:
    # Ej: BTN_vs_BB  |  BB_vs_BTN_SB
    v = [p for p in vill_positions if p]
    v_sorted = "_".join(sorted(v))
    if not v_sorted:
        return f"{hero_pos}_vs_NONE"
    return f"{hero_pos}_vs_{v_sorted}"


def run_quiet(pipeline: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input: dict del pipeline (main.run_pipeline_once)
    Output:
      - hero_player: 'p1'
      - hero_position: BTN/SB/BB/UNK
      - active_players: ['p1','p2',...]
      - n_players: int
      - is_heads_up: bool
      - situacion: string compacta (ej: 'BTN_vs_BB', 'BB_vs_BTN_SB')
    """
    dealer = str(pipeline.get("dealer") or "")
    pos = _positions_3max(dealer)

    stacks = {
        "p1": _safe_float(pipeline.get("p1stack"), 0.0),
        "p2": _safe_float(pipeline.get("p2stack"), 0.0),
        "p3": _safe_float(pipeline.get("p3stack"), 0.0),
    }
    active = _active_players(stacks)
    n = len(active)

    hero = "p1"
    hero_pos = pos.get(hero, "UNK")

    villains = [p for p in active if p != hero]
    villain_positions = [pos.get(p, "UNK") for p in villains]

    is_hu = (n == 2)

    situacion = _normalize_sit(hero_pos, villain_positions)

    return {
        "hero_player": hero,
        "hero_position": hero_pos,
        "active_players": active,
        "n_players": n,
        "is_heads_up": bool(is_hu),
        "situacion": situacion,
    }


if __name__ == "__main__":
    # Smoke manual opcional (solo al ejecutar este archivo)
    try:
        import main
        d = main.run_pipeline_once()
        s = run_quiet(d)
        print("situacion:", s.get("situacion"))
        print("hero_position:", s.get("hero_position"))
        print("active_players:", s.get("active_players"))
    except Exception as e:
        print("error:", e)
