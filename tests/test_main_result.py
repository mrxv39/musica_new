import pytest
import sys
from pathlib import Path

from musica_new import main

def get_latest_image(preflop_dir):
    exts = {".bmp", ".png", ".jpg", ".jpeg", ".webp"}
    files = [p for p in preflop_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None

def test_main_pipeline_result():
    root = Path(__file__).resolve().parent.parent
    preflop = root / "preflop"
    img = get_latest_image(preflop)
    if not img:
        pytest.skip("No images in preflop/")
    result = main.run_pipeline_once(str(img))
    assert isinstance(result["mano"], str) and len(result["mano"]) >= 2
    assert isinstance(result["time"], bool)
    assert isinstance(result["noboard"], bool)
    assert isinstance(result["dealer"], str)
