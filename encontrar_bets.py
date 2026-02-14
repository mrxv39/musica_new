# encontrar_bets.py
# ROIs legacy:
# - p1bet: (x1+388, y1+378, 50, 20)
# - p2bet: (x1+160, y1+220, 55, 20)
# - p3bet: (x1+565, y1+220, 50, 20)
# Guarda SOLO los ROI si OCR_DEBUG_BETS=1  -> preflop/crops/p1bet_roi.png, p2bet_roi.png, p3bet_roi.png

from pathlib import Path
import os
import re

import cv2
import pytesseract


THRESHOLD_BINARY = 200

ROI_P1BET = (388, 378, 50, 20)  # dx, dy, w, h
ROI_P2BET = (160, 220, 55, 20)
ROI_P3BET = (565, 220, 50, 20)


def _debug_enabled() -> bool:
    return os.getenv("OCR_DEBUG_BETS", "0") == "1"


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _extract_float(text: str) -> float:
    text = (text or "").replace(",", ".")
    m = re.search(r"\d+(\.\d+)?", text)
    return float(m.group(0)) if m else 0.0


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace(",", ".")
    text = re.sub(r"[^0-9.]+", "", text)
    if text.count(".") > 1:
        parts = text.split(".")
        text = parts[0] + "." + "".join(parts[1:])
    return text.strip(".")


def _quality_score(clean: str) -> int:
    if not clean:
        return 0
    score = len(clean)
    if "." in clean:
        score += 3
    return score


def _prep_roi(roi_gray):
    roi_up = cv2.resize(roi_gray, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_NEAREST)
    roi_blur = cv2.GaussianBlur(roi_up, (3, 3), 0)
    return roi_blur


def _ocr_best_value(roi_gray, cfg: str) -> float:
    roi_p = _prep_roi(roi_gray)

    _, thr = cv2.threshold(roi_p, THRESHOLD_BINARY, 255, cv2.THRESH_BINARY)
    txt1 = pytesseract.image_to_string(thr, config=cfg) or ""
    c1 = _clean_text(txt1)

    _, thr_inv = cv2.threshold(roi_p, THRESHOLD_BINARY, 255, cv2.THRESH_BINARY_INV)
    txt2 = pytesseract.image_to_string(thr_inv, config=cfg) or ""
    c2 = _clean_text(txt2)

    best_clean = c1 if _quality_score(c1) >= _quality_score(c2) else c2
    return float(_extract_float(best_clean))


def _ocr_roi(img_gray, x: int, y: int, w: int, h: int, roi_name: str, ocr_config: str) -> float:
    H, W = img_gray.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return 0.0

    roi = img_gray[y:y+h, x:x+w]

    if _debug_enabled():
        crops = Path("preflop") / "crops"
        crops.mkdir(exist_ok=True)
        cv2.imwrite(str(crops / roi_name), roi)

    return _ocr_best_value(roi, ocr_config)


def run_quiet(image_path: str, x1: int = 0, y1: int = 0):
    """
    Devuelve: (p1bet, p2bet, p3bet) float.
    Sin prints. Guarda SOLO ROI si OCR_DEBUG_BETS=1.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0, 0.0, 0.0

    cfg_num = "--psm 7 -c tessedit_char_whitelist=0123456789."

    dx, dy, w, h = ROI_P1BET
    p1 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, "p1bet_roi.png", cfg_num)

    dx, dy, w, h = ROI_P2BET
    p2 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, "p2bet_roi.png", cfg_num)

    dx, dy, w, h = ROI_P3BET
    p3 = _ocr_roi(img, x1 + dx, y1 + dy, w, h, "p3bet_roi.png", cfg_num)

    return p1, p2, p3


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        raise SystemExit(1)

    img_path = images[0]
    print("Using image:", img_path)

    os.environ["OCR_DEBUG_BETS"] = "1"
    p1, p2, p3 = run_quiet(str(img_path))

    print("P1BET:", p1)
    print("P2BET:", p2)
    print("P3BET:", p3)
