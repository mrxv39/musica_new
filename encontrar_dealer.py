# encontrar_dealer.py

from pathlib import Path
import cv2

THRESHOLD = 0.85


def list_images(preflop_dir: Path):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def choose_seat(center_xy, img_w, img_h):
    cx, cy = center_xy

    p2_anchor = (0.0, 0.0)
    p3_anchor = (float(img_w), 0.0)
    p1_anchor = (float(img_w) / 2.0, float(img_h))

    def d2(a):
        ax, ay = a
        return (cx - ax) ** 2 + (cy - ay) ** 2

    d_p2 = d2(p2_anchor)
    d_p3 = d2(p3_anchor)
    d_p1 = d2(p1_anchor)

    if d_p2 <= d_p3 and d_p2 <= d_p1:
        return False, True, False
    if d_p3 <= d_p2 and d_p3 <= d_p1:
        return False, False, True
    return True, False, False


def find_dealer_in_image(img_gray, tpl_gray, threshold=THRESHOLD):
    if tpl_gray.shape[0] > img_gray.shape[0] or tpl_gray.shape[1] > img_gray.shape[1]:
        return {"found": False, "score": 0.0, "center": None,
                "p1dealer": False, "p2dealer": False, "p3dealer": False}

    res = cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    found = max_val >= threshold

    if not found:
        return {"found": False, "score": float(max_val), "center": None,
                "p1dealer": False, "p2dealer": False, "p3dealer": False}

    th, tw = tpl_gray.shape[:2]
    top_left = (int(max_loc[0]), int(max_loc[1]))
    center = (top_left[0] + tw / 2.0, top_left[1] + th / 2.0)

    H, W = img_gray.shape[:2]
    p1, p2, p3 = choose_seat(center, W, H)

    return {
        "found": True,
        "score": float(max_val),
        "center": center,
        "p1dealer": p1,
        "p2dealer": p2,
        "p3dealer": p3,
    }


def run_quiet(image_path: str, threshold: float = THRESHOLD):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return False, False, False

    template_path = Path("preflop") / "templates" / "dealer.png"
    tpl = cv2.imread(str(template_path), cv2.IMREAD_GRAYSCALE)
    if tpl is None:
        return False, False, False

    result = find_dealer_in_image(img, tpl, threshold)
    return result["p1dealer"], result["p2dealer"], result["p3dealer"]


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    preflop = root / "preflop"
    crops = preflop / "crops"
    crops.mkdir(exist_ok=True)

    images = list_images(preflop)
    if not images:
        print("No image found in preflop/")
        exit()

    img_path = images[0]
    print("Using image:", img_path)

    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    tpl_path = preflop / "templates" / "dealer.png"
    tpl = cv2.imread(str(tpl_path), cv2.IMREAD_GRAYSCALE)

    if img is None or tpl is None:
        print("Error leyendo imagen o template.")
        exit()

    cv2.imwrite(str(crops / "dealer_roi.png"), img)

    result = find_dealer_in_image(img, tpl, THRESHOLD)

    print("DEALER encontrado:", result["found"])
    print("Score:", round(result["score"], 4))

    if result["found"]:
        who = "p1" if result["p1dealer"] else ("p2" if result["p2dealer"] else "p3")
        print("Dealer:", who)
