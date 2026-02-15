# C:\Users\Usuario\Desktop\projectos\musica_new\encontrar_move.py

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List


# =========================
# Paths / Store
# =========================

def default_store_path() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, "ui", "estrategias_store.json")


def load_store(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def iter_substrategies(store: dict) -> List[dict]:
    out = []
    for gname, items in store.items():
        if not isinstance(items, list):
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            payload = it.get("payload", {})
            if not isinstance(payload, dict):
                continue
            out.append({"global": gname, "id": it.get("id", ""), "payload": payload})
    return out


# =========================
# Matching helpers
# =========================

def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip().replace(",", ".")
        if s == "":
            return default
        return float(s)
    except Exception:
        return default


def _in_range(x: float, lo: float, hi: float) -> bool:
    return lo <= x <= hi


def _get_range(payload: dict, base: str) -> Tuple[Optional[float], Optional[float]]:
    """
    base: e.g. "p1_bet", "p2_stack"
    Acepta:
      - base_min/base_max
      - o base (valor fijo legacy) -> lo=hi=base
    Si no hay nada, devuelve (None, None)
    """
    kmin = f"{base}_min"
    kmax = f"{base}_max"
    if kmin in payload or kmax in payload:
        lo = _safe_float(payload.get(kmin, 0.0), 0.0)
        hi = _safe_float(payload.get(kmax, lo), lo)
        if lo > hi:
            hi = lo
        return lo, hi

    if base in payload:
        v = _safe_float(payload.get(base), 0.0)
        return v, v

    return None, None


def _match_string(state: dict, payload: dict, key: str) -> Tuple[bool, int]:
    """
    True/False y peso (1) si aplica.
    Si state no trae el campo -> no fuerza match.
    """
    if key not in state or state.get(key) in (None, ""):
        return True, 0
    sv = str(state.get(key)).strip()
    pv = str(payload.get(key, "")).strip()
    return (sv == pv), 1


def _match_number_in_payload_range(state: dict, payload: dict, state_key: str, payload_base: str) -> Tuple[bool, int, float]:
    """
    Match si el número en state[state_key] cae dentro del rango definido en payload para payload_base.
    Devuelve: (ok, peso, especificidad)
    """
    if state_key not in state or state.get(state_key) in (None, ""):
        return True, 0, 0.0

    x = _safe_float(state.get(state_key), 0.0)
    lo, hi = _get_range(payload, payload_base)
    if lo is None or hi is None:
        return True, 0, 0.0

    ok = _in_range(x, lo, hi)
    width = max(0.0, float(hi - lo))
    spec = 1.0 / (1.0 + width)
    return ok, 1, spec


@dataclass
class MatchResult:
    ok: bool
    score: int
    specificity: float
    item: Optional[dict] = None


def match_one(state: dict, item: dict) -> MatchResult:
    payload = item["payload"]

    score = 0
    spec = 0.0

    # claves de igualdad si están presentes en state
    for k in ("estrategia_global", "spot", "p1_position", "p2_position", "p3_position", "p2_tipo", "p3_tipo", "situacion"):
        ok, w = _match_string(state, payload, k)
        if not ok:
            return MatchResult(False, 0, 0.0)
        score += w

    # numéricos
    numeric_rules = [
        ("p1_bet", "p1_bet"),
        ("p2_bet", "p2_bet"),
        ("p3_bet", "p3_bet"),
        ("p1_stack", "p1_stack"),
        ("p2_stack", "p2_stack"),
        ("p3_stack", "p3_stack"),
        ("stackefectivo", "p1_stackef"),  # state usa stackefectivo, payload usa p1_stackef_min/max
    ]

    for sk, pb in numeric_rules:
        ok, w, s = _match_number_in_payload_range(state, payload, sk, pb)
        if not ok:
            return MatchResult(False, 0, 0.0)
        score += w
        spec += s

    return MatchResult(True, score, spec, item=item)


def find_best_match(state: dict, store_path: Optional[str] = None) -> Optional[dict]:
    path = store_path or default_store_path()
    store = load_store(path)
    items = iter_substrategies(store)

    best: Optional[MatchResult] = None
    for it in items:
        mr = match_one(state, it)
        if not mr.ok:
            continue
        if best is None:
            best = mr
            continue
        if mr.score > best.score:
            best = mr
        elif mr.score == best.score and mr.specificity > best.specificity:
            best = mr

    return best.item if best else None


# =========================
# MOVE selection (by hand membership) + fallback
# =========================

MOVE_BLOCKS_PRIORITY = [
    "open_push",
    "or_to_push",
    "or_to_call_small",
    "or_to_fold",
]


def normalize_hand(hand: Any) -> str:
    """
    Canonical:
      - Ranks uppercase
      - suitedness lowercase: s/o
    Examples:
      "83O" -> "83o"
      "KQS" -> "KQs"
      "aa"  -> "AA"
    """
    s = str(hand or "").strip()
    if not s:
        return ""
    s = s.replace(" ", "")

    # pares AA
    if len(s) == 2:
        return s[0].upper() + s[1].upper()

    # suited/off
    if len(s) == 3:
        r1 = s[0].upper()
        r2 = s[1].upper()
        t = s[2].lower()
        if t not in ("s", "o"):
            t = s[2].upper()  # fallback (pero esperamos s/o)
        return f"{r1}{r2}{t if isinstance(t,str) else 'o'}".replace("S", "s").replace("O", "o")

    # si llega algo raro, devuélvelo normalizado lo mejor posible
    return s.upper().replace("S", "s").replace("O", "o")


def _get_block_payload(payload: dict, key_prefix: str) -> dict:
    return {
        "block": key_prefix,
        "range": (payload.get(key_prefix) or "").strip(),
        "move": (payload.get(f"{key_prefix}_move") or "").strip(),
        "value_min": _safe_float(payload.get(f"{key_prefix}_value_min", 0.0), 0.0),
        "value_max": _safe_float(payload.get(f"{key_prefix}_value_max", 0.0), 0.0),
        "hands": payload.get(f"{key_prefix}_hands", []) or [],
    }


def choose_move_from_payload(state: dict, payload: dict) -> dict:
    """
    Reglas (v0.5.0 real):
      - Selecciona bloque por pertenencia de MANO al rango expandido ( *_hands ).
      - Prioridad: open_push > or_to_push > or_to_call_small > or_to_fold
      - Si NO hay match en ningún bloque -> fallback:
            move=FOLD, value_min=0.0, value_max=0.0, block="fallback"
    """
    mano = normalize_hand(state.get("mano", ""))

    blocks = [_get_block_payload(payload, k) for k in MOVE_BLOCKS_PRIORITY]

    # Si no hay mano en state, no podemos hacer match por mano -> fallback
    if not mano:
        return {
            "block": "fallback",
            "move": "FOLD",
            "value_min": 0.0,
            "value_max": 0.0,
            "range": "",
            "matched_by": "fallback_missing_mano",
        }

    for b in blocks:
        hands = b.get("hands", [])
        if not isinstance(hands, list):
            continue

        # normaliza hands al vuelo
        hands_norm = {normalize_hand(x) for x in hands}
        if mano in hands_norm:
            return {
                "block": b["block"],
                "move": b["move"],
                "value_min": float(b["value_min"]),
                "value_max": float(b["value_max"]),
                "range": b["range"],
                "matched_by": "mano",
                "mano": mano,
            }

    # fallback duro (lo que has pedido)
    return {
        "block": "fallback",
        "move": "FOLD",
        "value_min": 0.0,
        "value_max": 0.0,
        "range": "",
        "matched_by": "fallback",
        "mano": mano,
    }


def encontrar_move(state: dict, store_path: Optional[str] = None) -> dict:
    """
    Función principal:
      - busca subestrategia
      - decide move por mano
      - si no hay match de subestrategia -> fallback duro también
    """
    match = find_best_match(state, store_path=store_path)
    if not match:
        return {
            "match": None,
            "move": {
                "block": "fallback",
                "move": "FOLD",
                "value_min": 0.0,
                "value_max": 0.0,
                "range": "",
                "matched_by": "fallback_no_substrategy",
            },
        }

    payload = match["payload"]
    move_info = choose_move_from_payload(state, payload)

    return {
        "match": {
            "global": match.get("global"),
            "id": match.get("id"),
            "situacion": payload.get("situacion"),
            "spot": payload.get("spot"),
        },
        "move": move_info,
    }


# =========================
# CLI
# =========================

def _load_state_from_arg(s: str) -> dict:
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _load_state_from_file(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser(description="Busca subestrategia y devuelve move/value según state.")
    ap.add_argument("--store", default=default_store_path(), help="Ruta a ui/estrategias_store.json")
    ap.add_argument("--state_json", default="", help="State como JSON en string")
    ap.add_argument("--state_file", default="", help="Ruta a JSON con state")
    args = ap.parse_args()

    state = {}
    if args.state_file:
        state = _load_state_from_file(args.state_file)
    elif args.state_json:
        state = _load_state_from_arg(args.state_json)

    if not state:
        print("ERROR: state vacío. Usa --state_file o --state_json.")
        raise SystemExit(2)

    res = encontrar_move(state, store_path=args.store)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
