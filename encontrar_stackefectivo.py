# encontrar_stackefectivo.py
# ROI legacy: (x1+265, y1+472, 72, 42)
# Guarda crop solo si OCR_DEBUG_STACK=1

from pathlib import Path
import os
import re

import cv2
import pytesseract

ROI_REL = (265, 472, 72, 42)  # dx, dy, w, h
THRESHOLD_BINARY = 100


def _debug_enabled() -> bool:
    return os.getenv("OCR_DEBUG_STACK", "0") == "1"


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _extract_float(text: str) -> float:
    text = (text or "").replace(",", ".")
    m = re.search(r"\d+(\.\d+)?", text)
    return float(m.group(0)) if m else 0.0


def run_quiet(image_path: str, x1: int = 0, y1: int = 0) -> float:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0

    dx, dy, w, h = ROI_REL
    x = int(x1 + dx)
    y = int(y1 + dy)

    H, W = img.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return 0.0

    roi = img[y:y+h, x:x+w]

    # Guardar crop solo si debug activo
    if _debug_enabled():
        crops = Path("preflop") / "crops"
        crops.mkdir(exist_ok=True)
        cv2.imwrite(str(crops / "stackefect_roi.png"), roi)

    _, thr = cv2.threshold(roi, THRESHOLD_BINARY, 255, cv2.THRESH_BINARY)

    txt = pytesseract.image_to_string(
        thr,
        config="--psm 7 -c tessedit_char_whitelist=0123456789.,"
    )

    return _extract_float(txt)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        raise SystemExit(1)

    img_path = images[0]
    print("Using image:", img_path)

    # Activa debug automáticamente en modo script
    os.environ["OCR_DEBUG_STACK"] = "1"

    value = run_quiet(str(img_path))

    print("STACKEFECT encontrado:", value)
