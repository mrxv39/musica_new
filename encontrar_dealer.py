# encontrar_dealer.py
# - Usa la imagen completa como ROI (toda la mesa)
# - Guarda dealer_roi.png (imagen completa)
# - Busca dealer.png dentro de esa ROI
# - Imprime si lo encuentra y el score
# - Decide p1/p2/p3 según cercanía a 3 anclas (TL, TR, bottom-center)

from pathlib import Path
import cv2

THRESHOLD = 0.85


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _choose_seat(center_xy, img_w, img_h):
    cx, cy = center_xy

    # Anchors
    p2_anchor = (0.0, 0.0)                         # top-left
    p3_anchor = (float(img_w), 0.0)                # top-right
    p1_anchor = (float(img_w) / 2.0, float(img_h)) # bottom-center

    def d2(a):
        ax, ay = a
        return (cx - ax) ** 2 + (cy - ay) ** 2

    dist_p2 = d2(p2_anchor)
    dist_p3 = d2(p3_anchor)
    dist_p1 = d2(p1_anchor)

    # El más cercano gana (exactamente uno True)
    if dist_p2 <= dist_p3 and dist_p2 <= dist_p1:
        return False, True, False   # p1, p2, p3
    if dist_p3 <= dist_p2 and dist_p3 <= dist_p1:
        return False, False, True
    return True, False, False


def main():
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"
    crops = preflop / "crops"
    crops.mkdir(exist_ok=True)

    template_path = preflop / "templates" / "dealer.png"
    if not template_path.exists():
        print("ERROR: no existe template:", template_path)
        return

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        return

    img_path = images[0]
    print("Using image:", img_path)

    # ROI = imagen completa
    img_full = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    tpl = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)

    if img_full is None or tpl is None:
        print("Error leyendo imagen o template.")
        return

    # Guardar "ROI" (toda la mesa)
    cv2.imwrite(str(crops / "dealer_roi.png"), img_full)

    H, W = img_full.shape[:2]

    if tpl.shape[0] > img_full.shape[0] or tpl.shape[1] > img_full.shape[1]:
        print("Template más grande que ROI.")
        return

    res = cv2.matchTemplate(img_full, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    found = max_val >= THRESHOLD

    print("DEALER encontrado:", found)
    print("Score:", round(max_val, 4))

    # Si no se encuentra, no imprimimos seat
    if not found:
        return

    th, tw = tpl.shape[:2]
    top_left = (int(max_loc[0]), int(max_loc[1]))
    center = (top_left[0] + tw / 2.0, top_left[1] + th / 2.0)

    p1dealer, p2dealer, p3dealer = _choose_seat(center, W, H)

    # Mantengo el estilo "simple": una línea final
    who = "p1" if p1dealer else ("p2" if p2dealer else "p3")
    print("Dealer:", who)


if __name__ == "__main__":
    main()
