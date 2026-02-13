# encontrar_noboard.py
# - Recorta ROI (120,200,200,200)
# - Guarda noboard_roi.png
# - Detecta NOBOARD por intensidad (negro) y uniformidad (std)
#   NO usa matchTemplate (porque no_board.png es plano a propósito)

from pathlib import Path
import cv2

ROI = (120, 200, 200, 200)

# Umbrales (ajustables)
MEAN_MAX = 35.0     # cuanto más bajo, más negro
STD_MAX  = 18.0     # cuanto más bajo, más uniforme

# Extra: porcentaje de píxeles "muy oscuros"
DARK_THR = 45       # pixel < DARK_THR se considera oscuro
DARK_MIN_RATIO = 0.85  # al menos 85% de píxeles oscuros


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def main():
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"
    crops = preflop / "crops"
    crops.mkdir(exist_ok=True)

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        return

    img_path = images[0]
    print("Using image:", img_path)

    img_full = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img_full is None:
        print("Error leyendo imagen.")
        return

    x, y, w, h = ROI
    H, W = img_full.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        print("ROI fuera de límites.")
        return

    roi = img_full[y:y+h, x:x+w]
    cv2.imwrite(str(crops / "noboard_roi.png"), roi)

    mean_val = float(roi.mean())
    std_val  = float(roi.std())

    dark_ratio = float((roi < DARK_THR).sum()) / float(roi.size)

    noboard = (mean_val <= MEAN_MAX) and (std_val <= STD_MAX) and (dark_ratio >= DARK_MIN_RATIO)

    print("NOBOARD encontrado:", noboard)
    print("Stats:",
          "mean=", round(mean_val, 2),
          "std=", round(std_val, 2),
          "dark_ratio=", round(dark_ratio, 3),
          f"(MEAN_MAX={MEAN_MAX}, STD_MAX={STD_MAX}, DARK_MIN_RATIO={DARK_MIN_RATIO})")


if __name__ == "__main__":
    main()
