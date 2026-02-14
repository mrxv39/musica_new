# main.py
# musica_new/main.py

from __future__ import annotations

from pathlib import Path
import io
import re
import contextlib

import cv2

import reconocer_mano
import encontrar_dealer


# ---- Config ----
TIME_ROI = (350, 470, 50, 15)
TIME_TEMPLATE = Path("preflop") / "templates" / "time.bmp"
TIME_THRESHOLD = 0.85

NOBOARD_ROI = (120, 200, 200, 200)
MEAN_MAX = 35.0
STD_MAX = 18.0
DARK_MIN_RATIO = 0.85
DARK_PIXEL_THRESH = 50  # umbral para contar "oscuro"


def _latest_image_path() -> str:
    preflop = Path(__file__).resolve().parent / "preflop"
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    imgs = [p for p in preflop.iterdir() if p.is_file() and p.suffix.lower() in exts]
    imgs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(imgs[0]) if imgs else ""


def _read_gray(image_path: str):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return img


def _crop(img_gray, roi):
    x, y, w, h = roi
    H, W = img_gray.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return None
    return img_gray[y:y+h, x:x+w]


def detectar_time_quiet(image_path: str) -> bool:
    img = _read_gray(image_path)
    if img is None:
        return False

    tpl = cv2.imread(str(TIME_TEMPLATE), cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        return False

    roi = _crop(img, TIME_ROI)
    if roi is None:
        return False

    if tpl.shape[0] > roi.shape[0] or tpl.shape[1] > roi.shape[1]:
        return False

    res = cv2.matchTemplate(roi, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return bool(max_val >= TIME_THRESHOLD)


def detectar_noboard_quiet(image_path: str) -> bool:
    img = _read_gray(image_path)
    if img is None:
        return False

    roi = _crop(img, NOBOARD_ROI)
    if roi is None:
        return False

    mean = float(roi.mean())
    std = float(roi.std())
    dark_ratio = float((roi < DARK_PIXEL_THRESH).mean())

    return (mean <= MEAN_MAX) and (std <= STD_MAX) and (dark_ratio >= DARK_MIN_RATIO)


def reconocer_mano_quiet(image_path: str) -> str:
    # 1) Si existe run_quiet úsalo
    if hasattr(reconocer_mano, "run_quiet"):
        try:
            out = reconocer_mano.run_quiet(image_path)
            return out if isinstance(out, str) else ""
        except Exception:
            pass

    # 2) Usa run(image_path) pero capturando prints y extrayendo "MANO = xxxx"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            ret = reconocer_mano.run(image_path)
        except TypeError:
            ret = reconocer_mano.run()

    # si devuelve string, úsala
    if isinstance(ret, str) and ret.strip():
        return ret.strip()

    text = buf.getvalue()

    # Busca patrón tipo "MANO = 3c8h"
    m = re.search(r"MANO\s*=\s*([0-9TJQKA][cdhs][0-9TJQKA][cdhs])", text, re.IGNORECASE)
    if m:
        return m.group(1).lower()

    # fallback: intenta encontrar dos cartas sueltas tipo "3c 8h"
    m2 = re.search(r"\b([0-9TJQKA][cdhs])\s*([0-9TJQKA][cdhs])\b", text, re.IGNORECASE)
    if m2:
        return (m2.group(1) + m2.group(2)).lower()

    return ""


def run_pipeline_once(image_path: str = "") -> dict:
    if not image_path:
        image_path = _latest_image_path()

    mano = reconocer_mano_quiet(image_path) if image_path else ""
    time_found = detectar_time_quiet(image_path) if image_path else False
    noboard_found = detectar_noboard_quiet(image_path) if image_path else False

    # dealer (usa tu módulo)
    p1d = p2d = p3d = False
    try:
        if hasattr(encontrar_dealer, "run_quiet") and image_path:
            p1d, p2d, p3d = encontrar_dealer.run_quiet(image_path)
    except Exception:
        p1d = p2d = p3d = False

    dealer = "p1" if p1d else ("p2" if p2d else ("p3" if p3d else ""))

    return {"mano": mano, "time": bool(time_found), "noboard": bool(noboard_found), "dealer": dealer}


def main():
    print("Starting musica_new...")
    result = run_pipeline_once()

    print("\n--- RESULT ---")
    print(f"mano: {result.get('mano','')}")
    print(f"time: {result.get('time', False)}")
    print(f"noboard: {result.get('noboard', False)}")
    print(f"dealer: {result.get('dealer','')}")


if __name__ == "__main__":
    main()
