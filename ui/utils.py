# ui/utils.py

from __future__ import annotations

import re


RANKS = "AKQJT98765432"


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


def _rank_index(r: str) -> int:
    r = (r or "").strip().upper()
    return RANKS.find(r)


_pair_range_re = re.compile(r"^([AKQJT98765432])\1-([AKQJT98765432])\2$", re.I)
_pair_single_re = re.compile(r"^([AKQJT98765432])\1$", re.I)


def parse_flopzilla_range(expr: str) -> list[str]:
    """
    Parser mínimo para rangos estilo FlopZilla.

    Soporta:
      - Pares: "AA", "KK"
      - Rangos de pares: "AA-99" => ["AA","KK","QQ","JJ","TT","99"]
      - Listas separadas por coma/espacio: "AA,KK  QQ"

    TODO (luego):
      - Suited/offsuit: AKs, AKo
      - Rangos tipo AJs-ATs, KQo-KJo, etc.
      - "+" (JJ+, AQs+), etc.
    """
    expr = (expr or "").strip().upper()
    if not expr:
        return []

    raw_tokens = []
    for part in expr.split(","):
        part = part.strip()
        if not part:
            continue
        raw_tokens.extend([t for t in part.split() if t.strip()])

    out: list[str] = []
    seen = set()

    def _add(tok: str):
        if tok not in seen:
            seen.add(tok)
            out.append(tok)

    for tok in raw_tokens:
        tok = tok.strip().upper()
        if not tok:
            continue

        m = _pair_range_re.match(tok)
        if m:
            hi = m.group(1).upper()
            lo = m.group(2).upper()
            i_hi = _rank_index(hi)
            i_lo = _rank_index(lo)
            if i_hi == -1 or i_lo == -1:
                _add(tok)
                continue

            # slice canónico desde hi -> lo si hi es más fuerte (más a la izquierda)
            if i_hi <= i_lo:
                rng = RANKS[i_hi : i_lo + 1]
            else:
                rng = RANKS[i_lo : i_hi + 1]

            for r in rng:
                _add(r + r)
            continue

        m2 = _pair_single_re.match(tok)
        if m2:
            r = m2.group(1).upper()
            _add(r + r)
            continue

        # fallback: guardamos el token tal cual (para ampliar parser luego)
        _add(tok)

    return out
