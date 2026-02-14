# ui/ranges.py
from __future__ import annotations

from tkinter import ttk

from .constants import STACK_MIN, STACK_MAX
from .utils import safe_float


def coerce_range_stack(wmin: ttk.Spinbox, wmax: ttk.Spinbox) -> tuple[float, float]:
    vmin = safe_float(wmin.get(), 0.0)
    vmax = safe_float(wmax.get(), 0.0)

    if vmin < STACK_MIN:
        vmin = STACK_MIN
    if vmax < STACK_MIN:
        vmax = STACK_MIN
    if vmin > STACK_MAX:
        vmin = STACK_MAX
    if vmax > STACK_MAX:
        vmax = STACK_MAX
    if vmin > vmax:
        vmax = vmin

    wmin.delete(0, "end")
    wmin.insert(0, f"{vmin:.1f}")
    wmax.delete(0, "end")
    wmax.insert(0, f"{vmax:.1f}")
    return vmin, vmax
