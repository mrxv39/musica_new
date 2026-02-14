# ui/widgets.py

from __future__ import annotations

from tkinter import ttk


def build_filterable_combobox(
    parent: ttk.Frame,
    *,
    values: list[str],
    width: int = 22,
    default: str = "",
) -> ttk.Combobox:
    all_values = list(values)

    cb = ttk.Combobox(parent, values=all_values, state="normal", width=width)
    if default:
        cb.set(default)

    def _filter(_evt=None):
        q = (cb.get() or "").strip().lower()
        if not q:
            cb["values"] = all_values
            return
        cb["values"] = [v for v in all_values if q in v.lower()]

    def _reset(_evt=None):
        cb["values"] = all_values

    cb.bind("<KeyRelease>", _filter)
    cb.bind("<FocusIn>", _reset)
    return cb


def _make_spin(col: ttk.Frame, row: int, label: str, default: str, vmin: float, vmax: float) -> ttk.Spinbox:
    ttk.Label(col, text=label).grid(row=row, column=0, sticky="w", padx=6, pady=6)
    sp = ttk.Spinbox(col, from_=vmin, to=vmax, increment=0.5, width=10)
    sp.delete(0, "end")
    sp.insert(0, default)
    sp.grid(row=row, column=1, sticky="w", padx=6, pady=6)
    return sp


def build_hero_column(
    parent: ttk.Frame,
    *,
    positions: list[str],
    default_pos: str,
    # ranges
    default_bet_min: str,
    default_bet_max: str,
    default_stack_min: str,
    default_stack_max: str,
    default_se_min: str,
    default_se_max: str,
    pad: int,
    value_min: float,
    value_max: float,
    on_range_changed,
) -> tuple[ttk.Combobox, ttk.Spinbox, ttk.Spinbox, ttk.Spinbox, ttk.Spinbox, ttk.Spinbox, ttk.Spinbox]:
    """
    HERO:
      position
      bet_min/bet_max
      stack_min/stack_max
      stackef_min/stackef_max
    Returns:
      pos, bet_min, bet_max, stack_min, stack_max, se_min, se_max
    """
    col = ttk.LabelFrame(parent, text="HERO (p1)", padding=pad)
    col.columnconfigure(1, weight=1)

    ttk.Label(col, text="position:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    pos = ttk.Combobox(col, values=positions, state="readonly", width=10)
    pos.set(default_pos)
    pos.grid(row=0, column=1, sticky="w", padx=6, pady=6)

    bmin = _make_spin(col, 1, "bet min:", default_bet_min, value_min, value_max)
    bmax = _make_spin(col, 2, "bet max:", default_bet_max, value_min, value_max)

    smin = _make_spin(col, 3, "stack min:", default_stack_min, value_min, value_max)
    smax = _make_spin(col, 4, "stack max:", default_stack_max, value_min, value_max)

    semin = _make_spin(col, 5, "stack ef min:", default_se_min, value_min, value_max)
    semax = _make_spin(col, 6, "stack ef max:", default_se_max, value_min, value_max)

    ttk.Label(col, text=f"{value_min}–{value_max}", foreground="gray").grid(
        row=7, column=0, columnspan=2, sticky="w", padx=6, pady=(0, 4)
    )

    def _changed(_evt=None):
        on_range_changed(bmin, bmax)
        on_range_changed(smin, smax)
        on_range_changed(semin, semax)

    for w in (bmin, bmax, smin, smax, semin, semax):
        w.bind("<FocusOut>", _changed)
        w.bind("<Return>", _changed)

    return pos, bmin, bmax, smin, smax, semin, semax


def build_villain_column(
    parent: ttk.Frame,
    *,
    title: str,  # "P2" / "P3"
    positions: list[str],
    default_pos: str,
    tipos: list[str],
    default_tipo: str,
    # ranges
    default_bet_min: str,
    default_bet_max: str,
    default_stack_min: str,
    default_stack_max: str,
    pad: int,
    value_min: float,
    value_max: float,
    on_range_changed,
) -> tuple[ttk.Combobox, ttk.Combobox, ttk.Spinbox, ttk.Spinbox, ttk.Spinbox, ttk.Spinbox]:
    """
    Villain:
      position
      tipo (combobox)
      bet_min/bet_max
      stack_min/stack_max
    Returns:
      pos, tipo, bet_min, bet_max, stack_min, stack_max
    """
    col = ttk.LabelFrame(parent, text=title, padding=pad)
    col.columnconfigure(1, weight=1)

    ttk.Label(col, text="position:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    pos = ttk.Combobox(col, values=positions, state="readonly", width=10)
    pos.set(default_pos)
    pos.grid(row=0, column=1, sticky="w", padx=6, pady=6)

    ttk.Label(col, text="tipo:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
    tipo = ttk.Combobox(col, values=tipos, state="readonly", width=14)
    tipo.set(default_tipo)
    tipo.grid(row=1, column=1, sticky="w", padx=6, pady=6)

    bmin = _make_spin(col, 2, "bet min:", default_bet_min, value_min, value_max)
    bmax = _make_spin(col, 3, "bet max:", default_bet_max, value_min, value_max)

    smin = _make_spin(col, 4, "stack min:", default_stack_min, value_min, value_max)
    smax = _make_spin(col, 5, "stack max:", default_stack_max, value_min, value_max)

    ttk.Label(col, text=f"{value_min}–{value_max}", foreground="gray").grid(
        row=6, column=0, columnspan=2, sticky="w", padx=6, pady=(0, 4)
    )

    def _changed(_evt=None):
        on_range_changed(bmin, bmax)
        on_range_changed(smin, smax)

    for w in (bmin, bmax, smin, smax):
        w.bind("<FocusOut>", _changed)
        w.bind("<Return>", _changed)

    return pos, tipo, bmin, bmax, smin, smax
