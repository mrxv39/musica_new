# tests/test_move_by_hand_and_fallback.py

from pathlib import Path
from encontrar_move import encontrar_move

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "ui" / "estrategias_store.json"

def _base_state(mano: str):
    return {
        "estrategia_global": "BASE",
        "spot": "BTN",
        "p1_position": "BTN",
        "p2_position": "SB",
        "p3_position": "BB",
        "p2_tipo": "fish",
        "p3_tipo": "fish",
        "p1_bet": 0.0,
        "p2_bet": 0.5,
        "p3_bet": 1.0,
        "p1_stack": 25.0,
        "p2_stack": 24.5,
        "p3_stack": 24.0,
        "stackefectivo": 25.0,
        "situacion": "BTN_vs_BB_SB",
        "mano": mano,
    }

def test_match_by_hand_is_case_insensitive_on_suitedness():
    state = _base_state("83o")
    res = encontrar_move(state, store_path=str(STORE))
    assert res["match"] is not None
    assert res["move"]["block"] == "or_to_push"
    assert res["move"]["move"] == "OR"
    assert res["move"]["matched_by"] == "mano"

def test_fallback_is_fold_zero_when_no_hand_matches():
    state = _base_state("72o")
    res = encontrar_move(state, store_path=str(STORE))
    assert res["match"] is not None
    assert res["move"]["block"] == "fallback"
    assert res["move"]["move"] == "FOLD"
    assert float(res["move"]["value_min"]) == 0.0
    assert float(res["move"]["value_max"]) == 0.0

