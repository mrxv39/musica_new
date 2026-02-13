# reconocer_mano.py
# - Lee la imagen más reciente dentro de ./preflop (bmp/png/jpg/jpeg/webp)
# - Recorta carta1/carta2 (y palos) desde esa imagen (NO mss)
# - Guarda crops sobreescribiendo en preflop/crops
# - Template matching "imagen dentro de imagen" con cv2.matchTemplate
# - DEBUG: imprime score de 3c/3d/3h/3s para carta1 y carta2

from __future__ import annotations

from pathlib import Path
from typing import Tuple, List, Dict
import sys

import cv2
import numpy as np
from PIL import Image


region_palo1  = (360, 405, 30, 40)
region_palo2  = (410, 405, 30, 40)
region_carta1 = (339, 408, 50, 35)
region_carta2 = (389, 408, 50, 35)

SUITS = ["c", "d", "h", "s"]
RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"]

THRESHOLD = 0.60


def _crop_pil(img: Image.Image, region: Tuple[int, int, int, int]) -> Image.Image:
    x, y, w, h = region
    return img.crop((x, y, x + w, y + h))


def _list_images(preflop_dir: Path) -> List[Path]:
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def _load_templates(preflop_dir: Path) -> List[Tuple[str, str, Path]]:
    base = preflop_dir / "templates" / "ranks"
    out: List[Tuple[str, str, Path]] = []
    for s in SUITS:
        folder = base / f"cartas{s}"
        if not folder.exists():
            continue
        for r in RANKS:
            p = folder / f"{r}.png"
            if p.exists():
                out.append((s, r, p))
    return out


def _best_match(crop_gray: np.ndarray, templates: List[Tuple[str, str, Path]]) -> Tuple[str, float, List[Tuple[str, float]]]:
    best_label = "UNKNOWN"
    best_score = -1.0
    scored_top: List[Tuple[str, float]] = []

    for suit, rank, path in templates:
        tpl = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if tpl is None or tpl.size == 0:
            continue

        # Si template es más grande que crop, skip
        if tpl.shape[0] > crop_gray.shape[0] or tpl.shape[1] > crop_gray.shape[1]:
            continue

        res = cv2.matchTemplate(crop_gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)

        label = f"{rank}{suit}"
        scored_top.append((label, float(max_val)))

        if max_val > best_score:
            best_score = float(max_val)
            best_label = label

    scored_top.sort(key=lambda t: t[1], reverse=True)
    return best_label, best_score, scored_top[:5]


def _score_specific_rank(crop_gray: np.ndarray, preflop_dir: Path, rank: str) -> Dict[str, float]:
    # Devuelve score por suit para ese rank (p.ej. 3c/3d/3h/3s), si existe y no se skippea
    base = preflop_dir / "templates" / "ranks"
    out: Dict[str, float] = {}
    for suit in SUITS:
        p = base / f"cartas{suit}" / f"{rank}.png"
        if not p.exists():
            out[suit] = float("nan")
            continue
        tpl = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if tpl is None or tpl.size == 0:
            out[suit] = float("nan")
            continue
        if tpl.shape[0] > crop_gray.shape[0] or tpl.shape[1] > crop_gray.shape[1]:
            out[suit] = float("nan")  # no comparable
            continue
        res = cv2.matchTemplate(crop_gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        out[suit] = float(max_val)
    return out


def run() -> None:
    root = Path(__file__).resolve().parent
    preflop_dir = root / "preflop"
    crops_dir = preflop_dir / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)

    images = _list_images(preflop_dir)
    if not images:
        print(f"No image found in preflop/: {preflop_dir}")
        print("Contenido actual de preflop/:")
        for p in sorted(preflop_dir.iterdir(), key=lambda x: x.name.lower()):
            print(" -", p.name)
        return

    img_path = images[0]
    print(f"Using image: {img_path}")

    img = Image.open(img_path).convert("RGB")

    palo1 = _crop_pil(img, region_palo1)
    palo2 = _crop_pil(img, region_palo2)
    carta1 = _crop_pil(img, region_carta1)
    carta2 = _crop_pil(img, region_carta2)

    palo1.save(crops_dir / "palo1.png")
    palo2.save(crops_dir / "palo2.png")
    carta1.save(crops_dir / "carta1.png")
    carta2.save(crops_dir / "carta2.png")

    templates = _load_templates(preflop_dir)
    if not templates:
        print(f"ERROR: no hay templates en {preflop_dir / 'templates' / 'ranks'}")
        return

    c1 = cv2.imread(str(crops_dir / "carta1.png"), cv2.IMREAD_GRAYSCALE)
    c2 = cv2.imread(str(crops_dir / "carta2.png"), cv2.IMREAD_GRAYSCALE)
    if c1 is None or c2 is None:
        print("ERROR: no se pudieron leer los crops guardados.")
        return

    # DEBUG: scores exactos para rank=3 en ambas cartas
    s3_c1 = _score_specific_rank(c1, preflop_dir, "3")
    s3_c2 = _score_specific_rank(c2, preflop_dir, "3")
    print("DEBUG rank=3 scores card1:", {f"3{k}": round(v, 4) if v == v else None for k, v in s3_c1.items()})
    print("DEBUG rank=3 scores card2:", {f"3{k}": round(v, 4) if v == v else None for k, v in s3_c2.items()})

    label1, score1, top1 = _best_match(c1, templates)
    label2, score2, top2 = _best_match(c2, templates)

    if score1 < THRESHOLD:
        label1 = "UNKNOWN"
    if score2 < THRESHOLD:
        label2 = "UNKNOWN"

    print("Top card1:", top1)
    print("Top card2:", top2)
    print("card1:", label1, round(score1, 4))
    print("card2:", label2, round(score2, 4))
    print("MANO =", f"{label1}{label2}")


def main() -> None:
    run()
