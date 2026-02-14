# ui/utils.py

from __future__ import annotations


def safe_float(s: str, default: float = 0.0) -> float:
    try:
        s = (s or "").strip().replace(",", ".")
        if s == "":
            return default
        return float(s)
    except Exception:
        return default


def normalize_sit(hero_pos: str, vill_positions: list[str]) -> str:
    v = [p for p in vill_positions if p]
    v_sorted = "_".join(sorted(v))
    if not v_sorted:
        return f"{hero_pos}_vs_NONE"
    return f"{hero_pos}_vs_{v_sorted}"


def compute_situacion_from_positions(p1_pos: str, p2_pos: str, p3_pos: str) -> str:
    hero_pos = (p1_pos or "UNK").strip()
    vill = []
    if p2_pos:
        vill.append(p2_pos.strip())
    if p3_pos:
        vill.append(p3_pos.strip())
    return normalize_sit(hero_pos, vill)


def make_sub_id(payload: dict) -> str:
    sit = payload.get("situacion", "UNK")
    spot = payload.get("spot", "")
    p1 = f"h{payload.get('p1_position','')}"
    b = f"b{payload.get('p1_bet',0)}-{payload.get('p2_bet',0)}-{payload.get('p3_bet',0)}"
    s = f"s{payload.get('p1_stack',0)}-{payload.get('p2_stack',0)}-{payload.get('p3_stack',0)}"
    if spot:
        return f"{spot}__{sit}__{p1}__{b}__{s}"
    return f"{sit}__{p1}__{b}__{s}"


def is_float_in_range(text: str, min_v: float, max_v: float) -> bool:
    """
    Tk validation helper:
    - allows empty string while editing
    - allows partial "0." while editing
    - rejects non-numeric
    - enforces min/max when parseable
    """
    t = (text or "").strip().replace(",", ".")
    if t == "":
        return True
    if t in (".", "-"):
        return False
    try:
        v = float(t)
    except Exception:
        return False
    return (min_v <= v <= max_v)
