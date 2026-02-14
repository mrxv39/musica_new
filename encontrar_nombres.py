# encontrar_nombres.py
# ROIs legacy:
# - p2name: (x1+50,  y1+178, 103, 18)
# - p3name: (x1+625, y1+178, 103, 18)
# Debug: guarda SOLO ROI si OCR_DEBUG_NAMES=1

from pathlib import Path
import os
import re

import cv2
import pytesseract


ROI_P2NAME = (50, 178, 103, 18)
ROI_P3NAME = (625, 178, 103, 18)

# fallback thresholds estilo stacks
THR_P2 = 220
THR_P3 = 220


def _debug_enabled() -> bool:
    return os.getenv("OCR_DEBUG_NAMES", "0") == "1"


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^A-Za-z0-9_\- ]+", "", text)
    return text.strip()


def _prep_roi(roi_gray):
    roi_up = cv2.resize(roi_gray, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_NEAREST)
    roi_blur = cv2.GaussianBlur(roi_up, (3, 3), 0)
    return roi_blur


def _ocr_text(img_bin, cfg: str) -> str:
    txt = pytesseract.image_to_string(img_bin, config=cfg) or ""
    return _clean_text(txt)


def _quality_score(text: str) -> int:
    if not text:
        return 0
    score = len(text)
    if re.search(r"[A-Za-z]", text):
        score += 5
    return score


def _ocr_best_value(roi_gray, fallback_thr: int, cfg: str) -> str:
    """
    Estrategia idéntica a stacks:
    1) OTSU binary + inv
    2) Si vacío -> fallback threshold fijo
    """

    roi_p = _prep_roi(roi_gray)

    # 1) OTSU
    _, otsu = cv2.threshold(roi_p, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, otsu_inv = cv2.threshold(roi_p, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    t1 = _ocr_text(otsu, cfg)
    t2 = _ocr_text(otsu_inv, cfg)

    best = t1 if _quality_score(t1) >= _quality_score(t2) else t2
    if best:
        return best

    # 2) fallback fijo
    _, thr = cv2.threshold(roi_p, fallback_thr, 255, cv2.THRESH_BINARY)
    _, thr_inv = cv2.threshold(roi_p, fallback_thr, 255, cv2.THRESH_BINARY_INV)

    t3 = _ocr_text(thr, cfg)
    t4 = _ocr_text(thr_inv, cfg)

    return t3 if _quality_score(t3) >= _quality_score(t4) else t4


def _ocr_roi(img_gray, x: int, y: int, w: int, h: int, fallback_thr: int, roi_name: str, cfg: str) -> str:
    H, W = img_gray.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return ""

    roi = img_gray[y:y+h, x:x+w]

    if _debug_enabled():
        crops = Path("preflop") / "crops"
        crops.mkdir(exist_ok=True)
        cv2.imwrite(str(crops / roi_name), roi)

    return _ocr_best_value(roi, fallback_thr, cfg)


def run_quiet(image_path: str, x1: int = 0, y1: int = 0):
    """
    Devuelve: (p2name, p3name) str
    Sin prints. Guarda SOLO ROI si OCR_DEBUG_NAMES=1.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return "", ""

    cfg_txt = "--psm 7"

    dx, dy, w, h = ROI_P2NAME
    p2 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, THR_P2, "p2name_roi.png", cfg_txt)

    dx, dy, w, h = ROI_P3NAME
    p3 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, THR_P3, "p3name_roi.png", cfg_txt)

    return p2, p3


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        raise SystemExit(1)

    img_path = images[0]
    print("Using image:", img_path)

    os.environ["OCR_DEBUG_NAMES"] = "1"
    p2, p3 = run_quiet(str(img_path))

    print("P2NAME:", p2)
    print("P3NAME:", p3)
