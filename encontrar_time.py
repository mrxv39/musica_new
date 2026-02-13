# encontrar_time.py
# - Recorta ROI fija
# - Guarda time_roi.png
# - Busca time.bmp dentro de esa ROI
# - Imprime si lo encuentra y el score

from pathlib import Path
import cv2

ROI = (350, 470, 50, 15)
THRESHOLD = 0.85


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

    template_path = preflop / "templates" / "time.bmp"
    if not template_path.exists():
        print("ERROR: no existe template:", template_path)
        return

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        return

    img_path = images[0]
    print("Using image:", img_path)

    img_full = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    tpl = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)

    if img_full is None or tpl is None:
        print("Error leyendo imagen o template.")
        return

    x, y, w, h = ROI
    H, W = img_full.shape[:2]

    if x < 0 or y < 0 or x + w > W or y + h > H:
        print("ROI fuera de límites.")
        return

    roi = img_full[y:y+h, x:x+w]
    cv2.imwrite(str(crops / "time_roi.png"), roi)

    if tpl.shape[0] > roi.shape[0] or tpl.shape[1] > roi.shape[1]:
        print("Template más grande que ROI.")
        return

    res = cv2.matchTemplate(roi, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    found = max_val >= THRESHOLD

    print("TIME encontrado:", found)
    print("Score:", round(max_val, 4))


if __name__ == "__main__":
    main()
