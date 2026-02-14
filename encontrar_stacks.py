# encontrar_stacks.py
# ROIs legacy:
# - p2stack: (x1+70,  y1+198, 60, 18)
# - p3stack: (x1+645, y1+198, 60, 18)
# - p1stack: (x1+350, y1+485, 60, 18)
# Debug: guarda SOLO ROI si OCR_DEBUG_STACKS=1

from pathlib import Path
import os
import re

import cv2
import pytesseract


ROI_P2STACK = (70, 198, 60, 18)
ROI_P3STACK = (645, 198, 60, 18)
ROI_P1STACK = (350, 485, 60, 18)

# legacy thresholds (los dejamos como fallback)
THR_P2 = 230
THR_P3 = 250
THR_P1 = 250


def _debug_enabled() -> bool:
    return os.getenv("OCR_DEBUG_STACKS", "0") == "1"


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace(",", ".")
    text = re.sub(r"[^0-9.]+", "", text)
    if text.count(".") > 1:
        parts = text.split(".")
        text = parts[0] + "." + "".join(parts[1:])
    return text.strip(".")


def _parse_stack(clean: str) -> float:
    """
    Heurística útil:
    - Si viene '245' y no hay '.', asumimos 24.5 (pierde el punto).
    - Si viene '250' -> 25.0, etc.
    """
    if not clean:
        return 0.0

    if "." in clean:
        try:
            return float(clean)
        except Exception:
            return 0.0

    # sin punto: intenta entero
    try:
        n = int(clean)
    except Exception:
        return 0.0

    # caso típico: 3 dígitos (245 => 24.5)
    if 100 <= n <= 999:
        return n / 10.0

    return float(n)


def _prep_roi(roi_gray):
    roi_up = cv2.resize(roi_gray, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_NEAREST)
    roi_blur = cv2.GaussianBlur(roi_up, (3, 3), 0)
    return roi_blur


def _ocr_text(img_bin, cfg: str) -> str:
    txt = pytesseract.image_to_string(img_bin, config=cfg) or ""
    return _clean_text(txt)


def _ocr_best_value(roi_gray, fallback_thr: int, cfg: str) -> float:
    """
    Estrategia:
    1) Otsu (binary + inv) sobre ROI preprocesada
    2) Si sale 0.0, fallback a threshold fijo legacy (binary + inv)
    """
    roi_p = _prep_roi(roi_gray)

    # 1) OTSU normal/invertido
    _, otsu = cv2.threshold(roi_p, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, otsu_inv = cv2.threshold(roi_p, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    c1 = _ocr_text(otsu, cfg)
    c2 = _ocr_text(otsu_inv, cfg)

    v1 = _parse_stack(c1)
    v2 = _parse_stack(c2)

    best = v1 if v1 != 0.0 else v2
    if best != 0.0:
        return float(best)

    # 2) fallback threshold fijo legacy
    _, thr = cv2.threshold(roi_p, fallback_thr, 255, cv2.THRESH_BINARY)
    _, thr_inv = cv2.threshold(roi_p, fallback_thr, 255, cv2.THRESH_BINARY_INV)

    c3 = _ocr_text(thr, cfg)
    c4 = _ocr_text(thr_inv, cfg)

    v3 = _parse_stack(c3)
    v4 = _parse_stack(c4)

    return float(v3 if v3 != 0.0 else v4)


def _ocr_roi(img_gray, x: int, y: int, w: int, h: int, fallback_thr: int, roi_name: str, cfg: str) -> float:
    H, W = img_gray.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return 0.0

    roi = img_gray[y:y+h, x:x+w]

    if _debug_enabled():
        crops = Path("preflop") / "crops"
        crops.mkdir(exist_ok=True)
        cv2.imwrite(str(crops / roi_name), roi)

    return _ocr_best_value(roi, fallback_thr, cfg)


def run_quiet(image_path: str, x1: int = 0, y1: int = 0):
    """
    Devuelve: (p1stack, p2stack, p3stack) float.
    Sin prints. Guarda SOLO ROI si OCR_DEBUG_STACKS=1.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0, 0.0, 0.0

    cfg_num = "--psm 7 -c tessedit_char_whitelist=0123456789."

    dx, dy, w, h = ROI_P1STACK
    p1 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, THR_P1, "p1stack_roi.png", cfg_num)

    dx, dy, w, h = ROI_P2STACK
    p2 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, THR_P2, "p2stack_roi.png", cfg_num)

    dx, dy, w, h = ROI_P3STACK
    p3 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, THR_P3, "p3stack_roi.png", cfg_num)

    return float(p1), float(p2), float(p3)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        raise SystemExit(1)

    img_path = images[0]
    print("Using image:", img_path)

    os.environ["OCR_DEBUG_STACKS"] = "1"
    p1, p2, p3 = run_quiet(str(img_path))

    print("P1STACK:", p1)
    print("P2STACK:", p2)
    print("P3STACK:", p3)
