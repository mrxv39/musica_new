# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\pipeline\pipeline_runner.py

from __future__ import annotations

from dataclasses import dataclass

from workers.core.db import insert_hands_ocr
from workers.core.main_runner import run_main_json
from workers.core.signature import build_signature
from workers.core.types import TickCheck, WorkerPaths
from workers.core.utils.time_utils import dt_ms, now_s

from .override import override_mano_if_needed
from .dedupe import DedupeState


@dataclass(frozen=True)
class PipelineResult:
    ok: bool
    inserted: bool
    duplicate: bool
    duration_ms: int
    err: str = ""


def run_pipeline_once(
    mesa: int,
    paths: WorkerPaths,
    tick: TickCheck,
    dedupe: DedupeState,
) -> PipelineResult:
    """
    Ejecuta:
    - main --json
    - override mano si hace falta
    - dedupe por signature
    - insert DB
    """
    t0 = now_s()
    print(f"[mesa {mesa}] PIPELINE start")

    data, main_err = run_main_json(paths.main_py, tick.img_path, cwd=paths.root)
    if not data:
        return PipelineResult(ok=False, inserted=False, duplicate=False, duration_ms=dt_ms(t0), err=main_err or "main failed")

    changed = override_mano_if_needed(tick.mano, data)
    if changed:
        print(f"[mesa {mesa}] OVERRIDE mano -> {data.get('mano')}")

    sig = build_signature(mesa, data)
    if dedupe.is_duplicate(sig):
        return PipelineResult(ok=True, inserted=False, duplicate=True, duration_ms=dt_ms(t0))

    dedupe.update(sig)

    try:
        insert_hands_ocr(paths.db_path, mesa, data)
        print(f"[mesa {mesa}] INSERTED mano={data.get('mano')} move={data.get('move')} block={data.get('block')}")
        return PipelineResult(ok=True, inserted=True, duplicate=False, duration_ms=dt_ms(t0))
    except Exception as e:
        return PipelineResult(ok=False, inserted=False, duplicate=False, duration_ms=dt_ms(t0), err=f"DB INSERT FAILED: {e!r}")
