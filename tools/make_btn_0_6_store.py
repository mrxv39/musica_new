# tools/make_btn_0_6_store.py
import json
import os

CHART_PATH = os.path.join("engine","charts","nash_btn_3h_maxbb.json")
STORE_PATH = os.path.join("ui","estrategias_store.json")

TARGET_ID = "BTNvsSB_BB_FISH_FISH_0_6"
GLOBAL_NAME = "BASE"

# --- helper: chart rule intersects [0,6] ---
def intersects_0_6(rule):
    if rule is None:
        return False
    # number => [0, rule]
    if isinstance(rule, (int, float)):
        return rule > 0
    # [lo,hi]
    if isinstance(rule, list) and len(rule) == 2:
        lo, hi = float(rule[0]), float(rule[1])
        if hi < lo:
            lo, hi = hi, lo
        # intersects with [0,6]
        return not (hi < 0 or lo > 6)
    return False

def main():
    chart = json.load(open(CHART_PATH, "r", encoding="utf-8"))
    chart.pop("_meta", None)

    push_hands = sorted([k for k,v in chart.items() if intersects_0_6(v)])

    store = json.load(open(STORE_PATH, "r", encoding="utf-8"))
    if GLOBAL_NAME not in store or not isinstance(store[GLOBAL_NAME], list):
        store[GLOBAL_NAME] = []

    # remove existing with same id (idempotent)
    store[GLOBAL_NAME] = [it for it in store[GLOBAL_NAME] if it.get("id") != TARGET_ID]

    payload = {
        "spot": "BTN",
        "situacion": "SB_BB",
        "hero_position": "BTN",
        "p2_position": "SB",
        "p3_position": "BB",
        "p2_tipo": "FISH",
        "p3_tipo": "FISH",
        "stackefectivo_min": 0,
        "stackefectivo_max": 6,
        # Para que la UI "muestre algo", lo más útil es open_push con la lista
        "open_push": push_hands,
        "or_to_push": [],
        "or_to_call_small": [],
        "or_to_fold": []
    }

    store[GLOBAL_NAME].append({"id": TARGET_ID, "payload": payload})

    json.dump(store, open(STORE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("OK: created/updated", TARGET_ID, "hands:", len(push_hands))

if __name__ == "__main__":
    main()
