# C:\Users\Usuario\Desktop\projectos\musica_new\encontrar_move.py

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any, Optional, Tuple, List, Dict


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
# MOVE selection inside matched strategy
# =========================

MOVE_BLOCKS_PRIORITY = [
    "open_push",
    "or_to_push",
    "or_to_call_small",
    "or_to_fold",
]


def _get_state_value(state: dict) -> Optional[float]:
    """
    Valor numérico para decidir bloque por *_value_min/max.
    Acepta:
      - value
      - open_value
      - bet
      - p1_bet
    """
    for k in ("value", "open_value", "bet", "p1_bet"):
        if k in state and state.get(k) not in (None, ""):
            return _safe_float(state.get(k), None)  # type: ignore[arg-type]
    return None


def _get_block_payload(payload: dict, key_prefix: str) -> dict:
    return {
        "block": key_prefix,
        "range": (payload.get(key_prefix) or "").strip(),
        "move": (payload.get(f"{key_prefix}_move") or "").strip(),
        "value_min": _safe_float(payload.get(f"{key_prefix}_value_min", 0.0), 0.0),
        "value_max": _safe_float(payload.get(f"{key_prefix}_value_max", 0.0), 0.0),
    }


def choose_move_from_payload(state: dict, payload: dict) -> dict:
    """
    Devuelve:
      - si puede decidir: {"block","move","value_min","value_max","range"}
      - si no puede decidir: {"block":None, "reason":..., "blocks":[...]}
    Reglas:
      - si state trae selector_block (open_push/or_to_push/or_to_call_small/or_to_fold) -> usa ese bloque
      - si no, usa state.value (o alias) y escoge el primer bloque cuyo value_min<=value<=value_max
      - prioridad: open_push > or_to_push > or_to_call_small > or_to_fold
    """
    selector = (state.get("selector_block") or "").strip()
    if selector:
        if selector in MOVE_BLOCKS_PRIORITY:
            b = _get_block_payload(payload, selector)
            return {
                "block": b["block"],
                "move": b["move"],
                "value_min": b["value_min"],
                "value_max": b["value_max"],
                "range": b["range"],
            }
        return {"block": None, "reason": f"selector_block inválido: {selector}", "blocks": []}

    v = _get_state_value(state)
    blocks = [_get_block_payload(payload, k) for k in MOVE_BLOCKS_PRIORITY]

    # si no hay valor numérico para decidir, devolvemos resumen
    if v is None:
        return {
            "block": None,
            "reason": "Falta valor numérico en state (usa 'value' o 'open_value' o 'bet' o 'p1_bet')",
            "blocks": blocks,
        }

    # elegir por rango
    for b in blocks:
        lo = float(b["value_min"])
        hi = float(b["value_max"])
        if lo > hi:
            hi = lo
        # si bloque no está definido (sin move y sin range) lo saltamos
        if not b["move"] and not b["range"]:
            continue
        if _in_range(float(v), lo, hi):
            return {
                "block": b["block"],
                "move": b["move"],
                "value_min": lo,
                "value_max": hi,
                "range": b["range"],
                "state_value": float(v),
            }

    return {
        "block": None,
        "reason": f"Ningún bloque coincide con value={v}",
        "blocks": blocks,
    }


def encontrar_move(state: dict, store_path: Optional[str] = None) -> dict:
    """
    Función principal para llamar desde main.py:
      - busca subestrategia
      - decide move
      - devuelve dict compacto
    """
    match = find_best_match(state, store_path=store_path)
    if not match:
        return {"match": None, "move": None}

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
