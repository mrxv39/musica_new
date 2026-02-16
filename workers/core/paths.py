# workers/core/paths.py

from __future__ import annotations

from pathlib import Path

from .types import WorkerPaths


def build_paths() -> WorkerPaths:
    root = Path(__file__).resolve().parents[2]  # .../workers/core -> .../musica_new
    return WorkerPaths(
        root=root,
        db_path=root / "data" / "musica_new.db",
        out_dir=root / "preflop",
        main_py=root / "main.py",
    )


def mesa_image_path(paths: WorkerPaths, mesa: int) -> Path:
    return paths.out_dir / f"mesa{mesa}_current.bmp"
