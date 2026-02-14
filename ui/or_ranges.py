# ui/or_ranges.py
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, simpledialog

from .utils import parse_flopzilla_range, safe_float

# Colores exactos sacados de tus imágenes
COLOR_PUSH = "#00FFFF"       # OR_TO_PUSH (cyan)
COLOR_FOLD = "#FF7171"       # OR_TO_FOLD (rojo)
COLOR_OPEN_PUSH = "#00FF80"  # OPEN_PUSH (verde)
COLOR_CALL_SMALL = "#C082FF" # OR_TO_CALL_SMALL (lila)

MOVE_OPTIONS = ["OR", "PUSH", "FOLD"]
VALUE_MIN = 0.0
VALUE_MAX = 75.0
STEP = 0.5


def _clamp(v: float, lo: float, hi: float) -> float:
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


class _ORRow:
    """
    Una fila:
      - botón color (pegar rango)
      - texto rango (StringVar)
      - move (Combobox OR/PUSH/FOLD)
      - value min/max (Spinbox + botones +/-0.5)
    """
    def __init__(self, parent: ttk.Frame, *, row: int, label: str, bg: str):
        self.label = label

        self.range_var = tk.StringVar(value="")

        # botón pegar rango
        self.btn = tk.Button(
            parent,
            text=label,
            bg=bg,
            activebackground=bg,
            relief="raised",
            command=self._edit_range,
            width=18,
        )
        self.btn.grid(row=row, column=0, sticky="w", padx=6, pady=6)

        # texto rango pegado
        self.range_lbl = ttk.Label(parent, textvariable=self.range_var)
        self.range_lbl.grid(row=row, column=1, sticky="ew", padx=6, pady=6)

        # MOVE
        self.move_cb = ttk.Combobox(parent, values=MOVE_OPTIONS, state="readonly", width=6)
        self.move_cb.set("OR")
        self.move_cb.grid(row=row, column=2, sticky="w", padx=6, pady=6)

        # VALUE: controles precisos
        vbox = ttk.Frame(parent)
        vbox.grid(row=row, column=3, sticky="w", padx=6, pady=6)

        ttk.Label(vbox, text="min").grid(row=0, column=0, sticky="w")
        self.min_sp = ttk.Spinbox(vbox, from_=VALUE_MIN, to=VALUE_MAX, increment=STEP, width=6)
        self._set_spin(self.min_sp, VALUE_MIN)
        self.min_sp.grid(row=0, column=1, sticky="w", padx=(4, 6))

        self.btn_min_down = ttk.Button(vbox, text="-0.5", width=5, command=lambda: self._nudge(self.min_sp, -STEP))
        self.btn_min_up = ttk.Button(vbox, text="+0.5", width=5, command=lambda: self._nudge(self.min_sp, +STEP))
        self.btn_min_down.grid(row=0, column=2, sticky="w")
        self.btn_min_up.grid(row=0, column=3, sticky="w", padx=(4, 0))

        ttk.Label(vbox, text="max").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.max_sp = ttk.Spinbox(vbox, from_=VALUE_MIN, to=VALUE_MAX, increment=STEP, width=6)
        self._set_spin(self.max_sp, VALUE_MAX)
        self.max_sp.grid(row=1, column=1, sticky="w", padx=(4, 6), pady=(6, 0))

        self.btn_max_down = ttk.Button(vbox, text="-0.5", width=5, command=lambda: self._nudge(self.max_sp, -STEP))
        self.btn_max_up = ttk.Button(vbox, text="+0.5", width=5, command=lambda: self._nudge(self.max_sp, +STEP))
        self.btn_max_down.grid(row=1, column=2, sticky="w", pady=(6, 0))
        self.btn_max_up.grid(row=1, column=3, sticky="w", padx=(4, 0), pady=(6, 0))

        # coerción al salir/enter
        for w in (self.min_sp, self.max_sp):
            w.bind("<FocusOut>", lambda _e: self._coerce())
            w.bind("<Return>", lambda _e: self._coerce())

    def _edit_range(self):
        current = (self.range_var.get() or "").strip()
        s = simpledialog.askstring(
            title=self.label,
            prompt="Pega rango estilo FlopZilla (ej: AA-99, AA KK QQ):",
            initialvalue=current,
            parent=self.btn.winfo_toplevel(),
        )
        if s is None:
            return
        self.range_var.set((s or "").strip().upper())

    def _nudge(self, sp: ttk.Spinbox, delta: float):
        v = safe_float(sp.get(), 0.0)
        v = _clamp(v + delta, VALUE_MIN, VALUE_MAX)
        self._set_spin(sp, v)
        self._coerce()

    def _coerce(self):
        vmin = _clamp(safe_float(self.min_sp.get(), VALUE_MIN), VALUE_MIN, VALUE_MAX)
        vmax = _clamp(safe_float(self.max_sp.get(), VALUE_MAX), VALUE_MIN, VALUE_MAX)
        if vmin > vmax:
            vmax = vmin
        self._set_spin(self.min_sp, vmin)
        self._set_spin(self.max_sp, vmax)

    @staticmethod
    def _set_spin(sp: ttk.Spinbox, v: float):
        sp.delete(0, "end")
        sp.insert(0, f"{float(v):.1f}")

    # API

    def reset(self):
        self.range_var.set("")
        self.move_cb.set("OR")
        self._set_spin(self.min_sp, VALUE_MIN)
        self._set_spin(self.max_sp, VALUE_MAX)
        self._coerce()

    def load(self, payload: dict, *, key_prefix: str):
        self.range_var.set((payload.get(f"{key_prefix}") or "").strip().upper())

        mv = (payload.get(f"{key_prefix}_move") or "OR").strip().upper()
        if mv not in MOVE_OPTIONS:
            mv = "OR"
        self.move_cb.set(mv)

        vmin = payload.get(f"{key_prefix}_value_min", VALUE_MIN)
        vmax = payload.get(f"{key_prefix}_value_max", VALUE_MAX)
        try:
            vmin = float(vmin)
        except Exception:
            vmin = VALUE_MIN
        try:
            vmax = float(vmax)
        except Exception:
            vmax = VALUE_MAX

        vmin = _clamp(vmin, VALUE_MIN, VALUE_MAX)
        vmax = _clamp(vmax, VALUE_MIN, VALUE_MAX)
        if vmin > vmax:
            vmax = vmin

        self._set_spin(self.min_sp, vmin)
        self._set_spin(self.max_sp, vmax)
        self._coerce()

    def build_fields(self, *, key_prefix: str) -> dict:
        raw = (self.range_var.get() or "").strip().upper()

        mv = (self.move_cb.get() or "OR").strip().upper()
        if mv not in MOVE_OPTIONS:
            mv = "OR"

        self._coerce()
        vmin = float(safe_float(self.min_sp.get(), VALUE_MIN))
        vmax = float(safe_float(self.max_sp.get(), VALUE_MAX))
        if vmin > vmax:
            vmax = vmin

        return {
            key_prefix: raw,
            f"{key_prefix}_hands": parse_flopzilla_range(raw),
            f"{key_prefix}_move": mv,
            f"{key_prefix}_value_min": float(f"{vmin:.1f}"),
            f"{key_prefix}_value_max": float(f"{vmax:.1f}"),
        }


class ORRangesPanel:
    def __init__(self, parent: ttk.Frame, *, pad: int = 10):
        self.frame = ttk.LabelFrame(parent, text="Open Ranges (FlopZilla)", padding=pad)
        # columnas: btn | range text | move | value controls
        self.frame.columnconfigure(1, weight=1)

        ttk.Label(self.frame, text="Pulsa botón y pega rango (ej: AA-99).", foreground="gray").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 8)
        )
        ttk.Label(self.frame, text="MOVE", foreground="gray").grid(row=1, column=2, sticky="w", padx=6)
        ttk.Label(self.frame, text="VALUE (0.0–75.0)", foreground="gray").grid(row=1, column=3, sticky="w", padx=6)

        self.row_push = _ORRow(self.frame, row=2, label="OR_TO_PUSH", bg=COLOR_PUSH)
        self.row_fold = _ORRow(self.frame, row=3, label="OR_TO_FOLD", bg=COLOR_FOLD)
        self.row_call = _ORRow(self.frame, row=4, label="OR_TO_CALL_SMALL", bg=COLOR_CALL_SMALL)
        self.row_openpush = _ORRow(self.frame, row=5, label="OPEN_PUSH", bg=COLOR_OPEN_PUSH)

    def show(self):
        self.frame.grid()

    def hide(self):
        self.frame.grid_remove()

    def reset(self):
        self.row_push.reset()
        self.row_fold.reset()
        self.row_call.reset()
        self.row_openpush.reset()

    def load_from_payload(self, payload: dict):
        self.row_push.load(payload, key_prefix="or_to_push")
        self.row_fold.load(payload, key_prefix="or_to_fold")
        self.row_call.load(payload, key_prefix="or_to_call_small")
        self.row_openpush.load(payload, key_prefix="open_push")

    def build_payload_fields(self) -> dict:
        out = {}
        out.update(self.row_push.build_fields(key_prefix="or_to_push"))
        out.update(self.row_fold.build_fields(key_prefix="or_to_fold"))
        out.update(self.row_call.build_fields(key_prefix="or_to_call_small"))
        out.update(self.row_openpush.build_fields(key_prefix="open_push"))
        return out
