# musica_new/main.py

from __future__ import annotations

from pathlib import Path
import re
import io
import contextlib

import reconocer_mano
import encontrar_dealer
import encontrar_stackefectivo
import encontrar_bets
import encontrar_stacks
from encontrar_nombres import run_quiet as nombres_run
from encontrar_jugador import run_quiet as jugador_run
from encontrar_move import encontrar_move


# -------------------------------
# Helpers
# -------------------------------

def _latest_image_path() -> str:
    preflop = Path(__file__).resolve().parent / "preflop"
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    imgs = [p for p in preflop.iterdir() if p.is_file() and p.suffix.lower() in exts]
    imgs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(imgs[0]) if imgs else ""


def _get_mano(image_path: str) -> str:
    """
    Reconoce la mano.
    Si el módulo imprime pero no devuelve valor,
    extraemos MANO = XXXX del stdout.
    """
    mano = ""

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if hasattr(reconocer_mano, "run_quiet"):
            mano = reconocer_mano.run_quiet(image_path)
        elif hasattr(reconocer_mano, "run"):
            try:
                mano = reconocer_mano.run(image_path)
            except TypeError:
                mano = reconocer_mano.run()

    if not mano:
        txt = buf.getvalue()
        m = re.search(r"MANO\s*=\s*([0-9TJQKA][cdhs][0-9TJQKA][cdhs])", txt)
        if m:
            mano = m.group(1)

    return str(mano).strip()


def cards_to_notation(cards: str) -> str:
    """
    Convierte '3c8h' -> '83o'
    - Ordena por rango alto→bajo
    - 's' si suited, 'o' si offsuit
    - pares: 'AA'
    """
    s = (cards or "").strip()
    if len(s) != 4:
        return s

    r1, su1, r2, su2 = s[0].upper(), s[1].lower(), s[2].upper(), s[3].lower()

    order = {**{str(i): i for i in range(2, 10)}, "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
    v1 = order.get(r1, 0)
    v2 = order.get(r2, 0)

    # pares
    if r1 == r2:
        return f"{r1}{r2}"

    # ordenar
    if v2 > v1:
        r1, r2 = r2, r1
        su1, su2 = su2, su1

    suited = "s" if su1 == su2 else "o"
    return f"{r1}{r2}{suited}"


# -------------------------------
# Pipeline
# -------------------------------

def run_pipeline_once(image_path: str = "") -> dict:
    if not image_path:
        image_path = _latest_image_path()

    print(f"Using image: {image_path}")

    mano = _get_mano(image_path)

    # dealer
    p1d = p2d = p3d = False
    try:
        if hasattr(encontrar_dealer, "run_quiet"):
            p1d, p2d, p3d = encontrar_dealer.run_quiet(image_path)
    except Exception:
        pass

    dealer = "p1" if p1d else ("p2" if p2d else ("p3" if p3d else ""))

    # stack efectivo
    stackefectivo = 0.0
    try:
        if hasattr(encontrar_stackefectivo, "run_quiet"):
            stackefectivo = float(encontrar_stackefectivo.run_quiet(image_path))
    except Exception:
        pass

    # bets
    p1bet = p2bet = p3bet = 0.0
    try:
        if hasattr(encontrar_bets, "run_quiet"):
            p1bet, p2bet, p3bet = encontrar_bets.run_quiet(image_path)
            p1bet = float(p1bet)
            p2bet = float(p2bet)
            p3bet = float(p3bet)
    except Exception:
        pass

    # stacks
    p1stack = p2stack = p3stack = 0.0
    try:
        if hasattr(encontrar_stacks, "run_quiet"):
            p1stack, p2stack, p3stack = encontrar_stacks.run_quiet(image_path)
            p1stack = float(p1stack)
            p2stack = float(p2stack)
            p3stack = float(p3stack)
    except Exception:
        pass

    # tipos (opcional)
    p2tipo = p3tipo = ""
    try:
        p2name, p3name = nombres_run(image_path)
        p2tipo, p3tipo = jugador_run(p2name, p3name)
    except Exception:
        pass

    return {
        "mano": mano,
        "dealer": dealer,
        "stackefectivo": stackefectivo,
        "p1bet": p1bet,
        "p2bet": p2bet,
        "p3bet": p3bet,
        "p1stack": p1stack,
        "p2stack": p2stack,
        "p3stack": p3stack,
        "p2tipo": p2tipo,
        "p3tipo": p3tipo,
    }


# -------------------------------
# State builder
# -------------------------------

def build_state_from_pipeline(result: dict) -> dict:
    p1_pos = "BTN"
    p2_pos = "SB"
    p3_pos = "BB"

    return {
        "estrategia_global": "BASE",
        "spot": p1_pos,
        "p1_position": p1_pos,
        "p2_position": p2_pos,
        "p3_position": p3_pos,
        "p2_tipo": result.get("p2tipo", ""),
        "p3_tipo": result.get("p3tipo", ""),
        "p1_bet": result.get("p1bet", 0.0),
        "p2_bet": result.get("p2bet", 0.0),
        "p3_bet": result.get("p3bet", 0.0),
        "p1_stack": result.get("p1stack", 0.0),
        "p2_stack": result.get("p2stack", 0.0),
        "p3_stack": result.get("p3stack", 0.0),
        "stackefectivo": result.get("stackefectivo", 0.0),
        "situacion": "BTN_vs_BB_SB",

        # CLAVE: mano en notación (83o, KQs, AA, etc.)
        "mano": cards_to_notation(result.get("mano", "")),

        # legacy (si alguien lo usa en el futuro)
        "value": result.get("p1bet", 0.0),
    }


# -------------------------------
# Main
# -------------------------------

def main():
    print("Starting musica_new...")

    result = run_pipeline_once()
    state = build_state_from_pipeline(result)
    move_result = encontrar_move(state)

    print("\n--- REPORT ---")
    print(f"HERO position: {state['p1_position']}")
    print(f"MANO: {state.get('mano')}")
    print(f"stackefectivo: {result['stackefectivo']}")

    print("\nP2")
    print(f"  position: {state['p2_position']}")
    print(f"  stack: {result['p2stack']}")
    print(f"  bet: {result['p2bet']}")
    print(f"  tipo: {state['p2_tipo']}")

    print("\nP3")
    print(f"  position: {state['p3_position']}")
    print(f"  stack: {result['p3stack']}")
    print(f"  bet: {result['p3bet']}")
    print(f"  tipo: {state['p3_tipo']}")

    match = move_result.get("match")
    move = move_result.get("move")

    print("\nMOVE")
    if not match:
        print("  Subestrategia: (none)")
        print("  Move: (none)")
    else:
        print(f"  Subestrategia: {match.get('id')}")
        if move and move.get("block"):
            print(f"  Move: {move.get('move')}")
            print(f"  Value min: {move.get('value_min')}")
            print(f"  Value max: {move.get('value_max')}")
            print(f"  Block: {move.get('block')}")
            print(f"  Matched by: {move.get('matched_by')}")
        else:
            print("  Move: (none)")


if __name__ == "__main__":
    main()
