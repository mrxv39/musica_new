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
    """
    Genera un id humano y compacto para la subestrategia.

    Formato:
      {HERO}vs{V1}_{V2}_{P2TIPO}_{P3TIPO}_{STACK_MIN}_{STACK_MAX}

    Ej:
      BTNvsSB_BB_FISG_FISH_20_75
    """
    situ = (payload.get("situacion") or "").strip().upper()

    hero = "UNK"
    villains = []

    if "_VS_" in situ:
        left, right = situ.split("_VS_", 1)
        hero = (left or "UNK").strip().upper()
        villains = [v.strip().upper() for v in right.split("_") if v.strip()]
    else:
        hero = str(payload.get("hero_pos") or payload.get("hero") or "UNK").strip().upper()
        vlist = payload.get("villains") or payload.get("villanos") or []
        if isinstance(vlist, str):
            vlist = [x for x in vlist.split("_") if x.strip()]
        villains = [str(v).strip().upper() for v in vlist if str(v).strip()]

    # Orden determinista: SB antes BB (y el resto por detrás)
    order = {"SB": 0, "BB": 1, "BTN": 2, "CO": 3, "HJ": 4, "UTG": 5}
    villains = sorted(villains, key=lambda x: order.get(x, 999))
    vpart = "_".join(villains) if villains else "NONE"
    p2tipo = str(payload.get("p2tipo") or payload.get("p2_tipo") or payload.get("p2_type") or "UNK").strip().upper()
    p3tipo = str(payload.get("p3tipo") or payload.get("p3_tipo") or payload.get("p3_type") or "UNK").strip().upper()
    def _as_int(x, default=0):
        try:
            if x is None:
                return default
            if isinstance(x, bool):
                return int(x)
            if isinstance(x, (int, float)):
                return int(x)
            s = str(x).strip()
            if not s:
                return default
            return int(float(s))
        except Exception:
            return default
    stack_min = _as_int(payload.get("p1_stackef_min") or payload.get("stackef_min") or payload.get("p1_stack_min") or payload.get("stack_min"), 0)
    stack_max = _as_int(payload.get("p1_stackef_max") or payload.get("stackef_max") or payload.get("p1_stack_max") or payload.get("stack_max"), 0)
    return f"{hero}vs{vpart}_{p2tipo}_{p3tipo}_{stack_min}_{stack_max}"




_pair_range_re = re.compile(r"^([AKQJT98765432])\1-([AKQJT98765432])\2$", re.I)
_pair_single_re = re.compile(r"^([AKQJT98765432])\1$", re.I)




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

