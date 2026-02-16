# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\loop.py

from __future__ import annotations

from workers.core.capture import capture_region
from workers.core.detectors import detectar_mano, detectar_time, detectar_noboard
from workers.core.gate import gate_allows_pipeline
from workers.core.paths import mesa_image_path
from workers.core.types import TickCheck, WorkerPaths

from workers.core.pipeline.cooldown import Cooldown
from workers.core.pipeline.dedupe import DedupeState
from workers.core.pipeline.pipeline_runner import run_pipeline_once
from workers.core.pipeline.tick_logging import maybe_log_tick
from workers.core.pipeline.tick_state import TickState

from workers.core.utils.sleeping import sleep_short, sleep_interval, sleep_ms
from workers.core.utils.time_utils import now_s


COOLDOWN_AFTER_PIPELINE_MS = 900
COOLDOWN_AFTER_FAIL_MS = 600


def _do_capture(img_path, x1: int, y1: int, x2: int, y2: int) -> tuple[bool, str]:
    try:
        capture_region(x1, y1, x2, y2, img_path)
        return True, ""
    except Exception as e:
        return False, f"capture_error={e!r}"


def _run_checks(paths: WorkerPaths, img_path) -> tuple[str, str, bool, str, bool, str]:
    mano, mano_err = detectar_mano(paths.root, img_path)
    time_ok, time_err = detectar_time(paths.root, img_path)
    noboard_ok, noboard_err = detectar_noboard(paths.root, img_path)
    return mano, mano_err, time_ok, time_err, noboard_ok, noboard_err


def run_worker_loop(
    mesa: int,
    paths: WorkerPaths,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    interval_ms: int,
    log_every_ms: int,  # se mantiene en firma aunque ya no se usa para throttle
) -> int:
    busy = False

    cooldown = Cooldown()
    dedupe = DedupeState()

    # 🔒 LATCH: evita re-disparar pipeline mientras el gate siga TRUE
    armed = True

    # ✅ Tick spam killer: solo loguea cuando cambia el estado (cap/mano/time/noboard)
    tick_state = TickState()

    while True:
        now = now_s()

        # Cooldown: no ticks, no checks, nada
        if cooldown.active(now):
            if cooldown.should_log_once():
                print(f"[mesa {mesa}] cooldown {cooldown.remaining_ms(now)}ms")
            sleep_ms(120)
            continue

        img_path = mesa_image_path(paths, mesa)

        cap_ok, cap_err = _do_capture(img_path, x1, y1, x2, y2)
        mano, mano_err, time_ok, time_err, noboard_ok, noboard_err = _run_checks(paths, img_path)

        tick = TickCheck(
            cap_ok=cap_ok,
            cap_err=cap_err,
            mano=mano,
            mano_err=mano_err,
            time_ok=time_ok,
            time_err=time_err,
            noboard_ok=noboard_ok,
            noboard_err=noboard_err,
            img_path=img_path,
        )

        # Tick logging: SOLO si cambia el estado, y SOLO cuando gate FALSE, y nunca si busy
        maybe_log_tick(mesa, tick, busy, tick_state)

        if busy:
            sleep_ms(120)
            continue

        gate = gate_allows_pipeline(tick)

        # ✅ Rearme: cuando el gate vuelve a FALSE, permitimos el próximo disparo
        if not gate:
            armed = True
            sleep_short()
            continue

        # ✅ Gate TRUE pero ya disparado antes -> NO vuelvas a ejecutar main hasta reset
        if not armed:
            # Esperamos a que gate vuelva a FALSE
            sleep_ms(120)
            continue

        # Primer flanco gate FALSE->TRUE
        armed = False
        busy = True
        try:
            res = run_pipeline_once(mesa, paths, tick, dedupe)
            print(f"[mesa {mesa}] PIPELINE end {'OK' if res.ok else 'FAIL'} dt={res.duration_ms}ms")

            if not res.ok:
                if res.err:
                    print(res.err)
                cooldown.start_ms(COOLDOWN_AFTER_FAIL_MS)
            else:
                cooldown.start_ms(COOLDOWN_AFTER_PIPELINE_MS)

        finally:
            busy = False

        sleep_interval(interval_ms)

    # unreachable
