# engine/charts/nash_btn_3h.py
# BTN 3-handed Nash push/fold override chart loader (supports ranges).

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple, Union

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_PATH = os.path.join(_THIS_DIR, "nash_btn_3h_maxbb.json")

RangeRule = Union[None, float, int, Tuple[float, float], list]


def load_nash_btn_3h_chart(path: str = _DEFAULT_PATH) -> Dict[str, RangeRule]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data.pop("_meta", None)
        return data
    return {}


def _as_range(rule: Any) -> Optional[Tuple[float, float]]:
    """
    Normalize rule into (lo, hi):
      - number => (0, number)
      - [lo, hi] => (lo, hi)
      - None/invalid => None
    """
    if rule is None:
        return None

    # list/tuple range
    if isinstance(rule, (list, tuple)) and len(rule) == 2:
        try:
            lo = float(rule[0])
            hi = float(rule[1])
        except Exception:
            return None
        if hi < lo:
            lo, hi = hi, lo
        return (lo, hi)

    # number
    if isinstance(rule, (int, float)):
        hi = float(rule)
        if hi <= 0:
            return None
        return (0.0, hi)

    # string number
    if isinstance(rule, str):
        s = rule.strip().replace(",", ".")
        if not s:
            return None
        try:
            hi = float(s)
        except Exception:
            return None
        if hi <= 0:
            return None
        return (0.0, hi)

    return None


def nash_btn_3h_decision(hand_key: str, eff_bb: float, chart: Optional[Dict[str, RangeRule]] = None) -> bool:
    """
    Returns True => PUSH, False => FOLD

    Rule semantics:
      - If chart[hand_key] is a number: PUSH if eff_bb <= number
      - If chart[hand_key] is [lo, hi]: PUSH if lo <= eff_bb <= hi
      - Missing or None => FOLD
    """
    if eff_bb is None:
        return False
    try:
        eff = float(eff_bb)
    except Exception:
        return False

    if chart is None:
        chart = load_nash_btn_3h_chart()

    rule = chart.get(hand_key)
    r = _as_range(rule)
    if r is None:
        return False

    lo, hi = r
    return (lo <= eff <= hi)
