# workers/core/cli.py

from __future__ import annotations

import argparse

from .logging_utils import log_start
from .paths import build_paths
from .loop import run_worker_loop


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mesa", type=int, required=True)
    ap.add_argument("--x1", type=int, required=True)
    ap.add_argument("--y1", type=int, required=True)
    ap.add_argument("--x2", type=int, required=True)
    ap.add_argument("--y2", type=int, required=True)
    ap.add_argument("--interval-ms", type=int, default=1000)
    ap.add_argument("--log-every-ms", type=int, default=1000)
    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)

    paths = build_paths()

    log_start(args.mesa, paths, args.x1, args.y1, args.x2, args.y2)

    return run_worker_loop(
        mesa=args.mesa,
        paths=paths,
        x1=args.x1,
        y1=args.y1,
        x2=args.x2,
        y2=args.y2,
        interval_ms=args.interval_ms,
        log_every_ms=args.log_every_ms,
    )
