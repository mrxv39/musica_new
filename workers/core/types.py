# workers/core/types.py

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WorkerPaths:
    root: Path
    db_path: Path
    out_dir: Path
    main_py: Path


@dataclass(frozen=True)
class TickCheck:
    cap_ok: bool
    cap_err: str

    mano: str
    mano_err: str

    time_ok: bool
    time_err: str

    noboard_ok: bool
    noboard_err: str

    img_path: Path
