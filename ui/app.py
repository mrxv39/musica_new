# ui/app.py

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk, messagebox

from .constants import POSITIONS, ESTRATEGIAS_GLOBALES, SPOTS, STACK_MIN, STACK_MAX
from .utils import safe_float, compute_situacion_from_positions, make_sub_id
from .ranges import coerce_range_stack
from .or_ranges import ORRangesPanel
from .store import (
    load_store,
    save_store,
    ensure_global,
    list_subs,
    upsert_sub,
    delete_sub,
)
from .widgets import (
    build_filterable_combobox,
    build_hero_column,
    build_villain_column,
)

TIPOS = ["fish", "fish_pasivo", "fish_agresivo", "reg", "reg_pasivo", "reg_agresivo"]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("musica_new — Estrategias (UI)")
        self.geometry("1040x720")
        self.minsize(980, 680)

        self.store = load_store()
        self.current_global = ESTRATEGIAS_GLOBALES[0]
        ensure_global(self.store, self.current_global)
        self.current_sub_index: int | None = None

        self._build_ui()
        self._set_global(self.current_global)
        self.on_generate()

    # ================= UI =================
    def _open_nash_editor(self):
        """Open Nash Editor in a separate process (non-blocking)."""
        try:
            import subprocess, sys
            subprocess.Popen([sys.executable, "-m", "ui.nash_editor"])
        except Exception as e:
            try:
                from tkinter import messagebox
                messagebox.showerror("Error", f"No se pudo abrir Nash Editor:\n{e}")
            except Exception:
                pass

    def _build_ui(self):
        pad = 10

        root = ttk.Frame(self, padding=pad)
        root.pack(fill="both", expand=True)

        root.columnconfigure(0, weight=4)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=2)

        # MAIN TOP
        main_top = ttk.LabelFrame(root, text="Crear estrategia", padding=pad)
        main_top.grid(row=0, column=0, sticky="nsew", padx=(0, pad), pady=(0, pad))
        main_top.columnconfigure(0, weight=1)

        # Row 0: SPOT
        spot_row = ttk.Frame(main_top)
        spot_row.grid(row=0, column=0, sticky="ew")
        spot_row.columnconfigure(1, weight=1)

        ttk.Label(spot_row, text="spot:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.spot_combo = build_filterable_combobox(spot_row, values=SPOTS, width=22, default=SPOTS[0])
        self.spot_combo.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # Row 1: columns
        cols = ttk.Frame(main_top)
        cols.grid(row=1, column=0, sticky="nsew")
        cols.columnconfigure(0, weight=1)
        cols.columnconfigure(1, weight=1)
        cols.columnconfigure(2, weight=1)

        (
            self.p1_pos,
            self.p1_bet_min, self.p1_bet_max,
            self.p1_stack_min, self.p1_stack_max,
            self.p1_se_min, self.p1_se_max,
        ) = build_hero_column(
            cols,
            positions=POSITIONS,
            default_pos="BTN",
            default_bet_min="0.0",
            default_bet_max="75.0",
            default_stack_min="0.0",
            default_stack_max="75.0",
            default_se_min="0.0",
            default_se_max="75.0",
            pad=pad,
            value_min=STACK_MIN,
            value_max=STACK_MAX,
            on_range_changed=lambda a, b: coerce_range_stack(a, b),
        )
        self.p1_pos.master.grid(row=0, column=0, sticky="nsew", padx=(0, pad))

        (
            self.p2_pos,
            self.p2_tipo,
            self.p2_bet_min, self.p2_bet_max,
            self.p2_stack_min, self.p2_stack_max,
        ) = build_villain_column(
            cols,
            title="P2",
            positions=POSITIONS,
            default_pos="SB",
            tipos=TIPOS,
            default_tipo="fish",
            default_bet_min="0.0",
            default_bet_max="75.0",
            default_stack_min="0.0",
            default_stack_max="75.0",
            pad=pad,
            value_min=STACK_MIN,
            value_max=STACK_MAX,
            on_range_changed=lambda a, b: coerce_range_stack(a, b),
        )
        self.p2_pos.master.grid(row=0, column=1, sticky="nsew", padx=(0, pad))

        (
            self.p3_pos,
            self.p3_tipo,
            self.p3_bet_min, self.p3_bet_max,
            self.p3_stack_min, self.p3_stack_max,
        ) = build_villain_column(
            cols,
            title="P3",
            positions=POSITIONS,
            default_pos="BB",
            tipos=TIPOS,
            default_tipo="fish",
            default_bet_min="0.0",
            default_bet_max="75.0",
            default_stack_min="0.0",
            default_stack_max="75.0",
            pad=pad,
            value_min=STACK_MIN,
            value_max=STACK_MAX,
            on_range_changed=lambda a, b: coerce_range_stack(a, b),
        )
        self.p3_pos.master.grid(row=0, column=2, sticky="nsew")

        actions = ttk.Frame(main_top)
        actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        ttk.Button(actions, text="Generar", command=self.on_generate).pack(side="left")
        ttk.Button(actions, text="Guardar subestrategia", command=self.on_save_sub).pack(side="left", padx=(10, 0))
        ttk.Button(actions, text="Nuevo (limpiar)", command=self.on_new).pack(side="left", padx=(10, 0))
        ttk.Button(actions, text="Copiar JSON", command=self.on_copy).pack(side="left", padx=(10, 0))

        # OR panel (oculto hasta seleccionar subestrategia)
        self.or_panel = ORRangesPanel(main_top, pad=pad)
        self.or_panel.frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        self.or_panel.hide()

        # SIDEBAR
        sidebar = ttk.LabelFrame(root, text="Estrategias", padding=pad)
        sidebar.grid(row=0, column=1, rowspan=2, sticky="nsew")
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(3, weight=1)

        ttk.Label(sidebar, text="estrategia global:").grid(row=0, column=0, sticky="w", padx=6, pady=(0, 6))

        self.global_combo = ttk.Combobox(sidebar, values=ESTRATEGIAS_GLOBALES, state="readonly", width=28)
        self.global_combo.set(self.current_global)
        self.global_combo.grid(row=1, column=0, sticky="ew", padx=6, pady=(0, 10))
        self.global_combo.bind("<<ComboboxSelected>>", self._on_global_changed)

        ttk.Label(sidebar, text="subestrategias:").grid(row=2, column=0, sticky="w", padx=6, pady=(0, 6))

        self.sub_list = tk.Listbox(sidebar, height=10)
        self.sub_list.grid(row=3, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.sub_list.bind("<<ListboxSelect>>", self._on_sub_selected)

        sub_scroll = ttk.Scrollbar(sidebar, orient="vertical", command=self.sub_list.yview)
        self.sub_list.configure(yscrollcommand=sub_scroll.set)
        sub_scroll.grid(row=3, column=1, sticky="ns", pady=(0, 6))

        side_btns = ttk.Frame(sidebar)
        side_btns.grid(row=4, column=0, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(side_btns, text="Borrar subestrategia", command=self.on_delete_sub).pack(side="left")
        ttk.Button(side_btns, text="Refrescar", command=self.refresh_sub_list).pack(side="left", padx=(10, 0))

        # OUTPUT
        out = ttk.LabelFrame(root, text="Salida", padding=pad)
        out.grid(row=1, column=0, sticky="nsew", padx=(0, pad))
        out.columnconfigure(0, weight=1)
        out.rowconfigure(1, weight=1)

        self.lbl_info = ttk.Label(out, text="situacion: —", font=("Segoe UI", 12, "bold"))
        self.lbl_info.grid(row=0, column=0, sticky="w")

        self.txt = tk.Text(out, wrap="none")
        self.txt.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        yscroll = ttk.Scrollbar(out, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=yscroll.set)
        yscroll.grid(row=1, column=1, sticky="ns", pady=(8, 0))

    # ================= GLOBAL / LIST =================

    def _set_global(self, global_name: str):
        global_name = (global_name or "").strip() or ESTRATEGIAS_GLOBALES[0]
        self.current_global = global_name
        ensure_global(self.store, self.current_global)
        save_store(self.store)
        self.current_sub_index = None
        self.global_combo.set(self.current_global)
        self.refresh_sub_list()
        self.or_panel.hide()

    def refresh_sub_list(self):
        self.sub_list.delete(0, "end")
        for it in list_subs(self.store, self.current_global):
            self.sub_list.insert("end", it.get("id", "sub"))

    # ================= PAYLOAD =================

    def build_payload(self) -> dict:
        # coerce stack ranges
        for a, b in [
            (self.p1_bet_min, self.p1_bet_max),
            (self.p2_bet_min, self.p2_bet_max),
            (self.p3_bet_min, self.p3_bet_max),
            (self.p1_stack_min, self.p1_stack_max),
            (self.p2_stack_min, self.p2_stack_max),
            (self.p3_stack_min, self.p3_stack_max),
            (self.p1_se_min, self.p1_se_max),
        ]:
            coerce_range_stack(a, b)

        payload = {
            "estrategia_global": self.current_global,
            "spot": (self.spot_combo.get() or "").strip(),
            "p1_position": self.p1_pos.get().strip(),
            "p1_bet_min": safe_float(self.p1_bet_min.get(), 0.0),
            "p1_bet_max": safe_float(self.p1_bet_max.get(), 0.0),
            "p1_stack_min": safe_float(self.p1_stack_min.get(), 0.0),
            "p1_stack_max": safe_float(self.p1_stack_max.get(), 0.0),
            "p1_stackef_min": safe_float(self.p1_se_min.get(), 0.0),
            "p1_stackef_max": safe_float(self.p1_se_max.get(), 0.0),
            "p2_position": self.p2_pos.get().strip(),
            "p2_tipo": self.p2_tipo.get().strip(),
            "p2_bet_min": safe_float(self.p2_bet_min.get(), 0.0),
            "p2_bet_max": safe_float(self.p2_bet_max.get(), 0.0),
            "p2_stack_min": safe_float(self.p2_stack_min.get(), 0.0),
            "p2_stack_max": safe_float(self.p2_stack_max.get(), 0.0),
            "p3_position": self.p3_pos.get().strip(),
            "p3_tipo": self.p3_tipo.get().strip(),
            "p3_bet_min": safe_float(self.p3_bet_min.get(), 0.0),
            "p3_bet_max": safe_float(self.p3_bet_max.get(), 0.0),
            "p3_stack_min": safe_float(self.p3_stack_min.get(), 0.0),
            "p3_stack_max": safe_float(self.p3_stack_max.get(), 0.0),
        }

        # OR fields (solo si el panel está visible/seleccionado)
        payload.update(self.or_panel.build_payload_fields())

        payload["situacion"] = compute_situacion_from_positions(
            payload["p1_position"],
            payload["p2_position"],
            payload["p3_position"],
        )
        return payload

    # ================= ACTIONS =================

    def on_generate(self):
        payload = self.build_payload()
        self.lbl_info.config(
            text=f"spot: {payload.get('spot','—')} | situacion: {payload.get('situacion','—')} | global: {self.current_global}"
        )
        self.txt.delete("1.0", "end")
        self.txt.insert("end", json.dumps(payload, indent=2, ensure_ascii=False))


    def _sub_identity(self, payload: dict) -> tuple:
        # Campos clave (B): posiciones + tipos + stacks (stackef preferente)
        def pick(*keys, default=""):
            for k in keys:
                if k in payload and payload.get(k) is not None:
                    return payload.get(k)
            return default

        def U(x, default=""):
            s = str(x if x is not None else default).strip()
            return s.upper()

        def N(x, default=0.0):
            try:
                if x is None:
                    return float(default)
                return float(x)
            except Exception:
                try:
                    return float(str(x).strip())
                except Exception:
                    return float(default)

        spot = U(pick("spot", default=""))
        situ = U(pick("situacion", "situation", default=""))

        p1pos = U(pick("p1_position", "p1_pos", "hero_pos", "hero_position", "p1pos", default=""))
        p2pos = U(pick("p2_position", "p2_pos", "villain1_pos", "p2pos", default=""))
        p3pos = U(pick("p3_position", "p3_pos", "villain2_pos", "p3pos", default=""))

        p2tipo = U(pick("p2tipo", "p2_tipo", "p2_type", default="UNK"))
        p3tipo = U(pick("p3tipo", "p3_tipo", "p3_type", default="UNK"))

        smin = N(pick("p1_stackef_min", "stackef_min", "stack_min", "p1_stack_min", default=0.0), 0.0)
        smax = N(pick("p1_stackef_max", "stackef_max", "stack_max", "p1_stack_max", default=0.0), 0.0)

        return (spot, situ, p1pos, p2pos, p3pos, p2tipo, p3tipo, round(smin, 3), round(smax, 3))

    def on_save_sub(self):
        payload = self.build_payload()
        create_new = False  # bandera local: solo para este guardado
        # Si estamos editando y cambian campos clave, preguntar: actualizar vs crear nueva
        try:
            editing = (self.current_sub_index is not None)
            old_sig = getattr(self, '_selected_sub_identity', None)
            new_sig = self._sub_identity(payload)
            if editing and old_sig is not None and new_sig != old_sig:
                res = messagebox.askyesnocancel(
                    "Cambios detectados",
                    "Has cambiado campos clave.\n\n"
                    "Sí = actualizar la subestrategia actual\n"
                    "No = crear una nueva\n"
                    "Cancelar = no guardar"
                )
                if res is None:
                    return
                if res is False:
                    create_new = True
        except Exception:
            # Si falla la comparación, no bloqueamos el guardado
            pass
        sub_id = make_sub_id(payload)
        idx = upsert_sub(self.store, self.current_global, sub_id, payload)
        save_store(self.store)

        self.current_sub_index = idx
        self.refresh_sub_list()
        self.sub_list.selection_clear(0, "end")
        self.sub_list.selection_set(idx)

        messagebox.showinfo("OK", "Subestrategia guardada/actualizada.")

    def on_delete_sub(self):
        sel = self.sub_list.curselection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona una subestrategia para borrar.")
            return
        idx = int(sel[0])

        delete_sub(self.store, self.current_global, idx)
        save_store(self.store)
        self.current_sub_index = None
        self.refresh_sub_list()
        self.or_panel.hide()
        self.on_generate()

    def _on_global_changed(self, _evt=None):
        self._set_global(self.global_combo.get())

    def _on_sub_selected(self, _evt=None):
        sel = self.sub_list.curselection()
        if not sel:
            return
        idx = int(sel[0])

        items = list_subs(self.store, self.current_global)
        if not (0 <= idx < len(items)):
            return

        payload = items[idx].get("payload", {})
        if not isinstance(payload, dict):
            return

        if "spot" in payload:
            self.spot_combo.set(payload.get("spot", SPOTS[0]))

        self.p1_pos.set(payload.get("p1_position", "BTN"))
        self.p2_pos.set(payload.get("p2_position", "SB"))
        self.p3_pos.set(payload.get("p3_position", "BB"))
        self.p2_tipo.set(payload.get("p2_tipo", "fish"))
        self.p3_tipo.set(payload.get("p3_tipo", "fish"))

        def _get(k, fallback):
            return payload.get(k, fallback)

        # bet (compat)
        p1b = payload.get("p1_bet", _get("p1_bet_min", 0.0))
        p2b = payload.get("p2_bet", _get("p2_bet_min", 0.0))
        p3b = payload.get("p3_bet", _get("p3_bet_min", 0.0))
        self._set_entry(self.p1_bet_min, _get("p1_bet_min", p1b))
        self._set_entry(self.p1_bet_max, _get("p1_bet_max", p1b))
        self._set_entry(self.p2_bet_min, _get("p2_bet_min", p2b))
        self._set_entry(self.p2_bet_max, _get("p2_bet_max", p2b))
        self._set_entry(self.p3_bet_min, _get("p3_bet_min", p3b))
        self._set_entry(self.p3_bet_max, _get("p3_bet_max", p3b))

        # stack (compat)
        p1s = payload.get("p1_stack", _get("p1_stack_min", 0.0))
        p2s = payload.get("p2_stack", _get("p2_stack_min", 0.0))
        p3s = payload.get("p3_stack", _get("p3_stack_min", 0.0))
        self._set_entry(self.p1_stack_min, _get("p1_stack_min", p1s))
        self._set_entry(self.p1_stack_max, _get("p1_stack_max", p1s))
        self._set_entry(self.p2_stack_min, _get("p2_stack_min", p2s))
        self._set_entry(self.p2_stack_max, _get("p2_stack_max", p2s))
        self._set_entry(self.p3_stack_min, _get("p3_stack_min", p3s))
        self._set_entry(self.p3_stack_max, _get("p3_stack_max", p3s))

        # stack efectivo hero (compat)
        se = payload.get("stackefectivo", _get("p1_stackef_min", 0.0))
        self._set_entry(self.p1_se_min, _get("p1_stackef_min", se))
        self._set_entry(self.p1_se_max, _get("p1_stackef_max", se))

        # OR ranges (strings)
        self.or_panel.load_from_payload(payload)
        self.or_panel.show()

        self.current_sub_index = idx
        # Snapshot (para detectar cambios clave)
        try:
            items = self.store.get(self.current_global, [])
            if 0 <= idx < len(items):
                self._selected_sub_id = items[idx].get('id')
                self._selected_sub_identity = self._sub_identity(items[idx].get('payload', {}))
        except Exception:
            self._selected_sub_id = None
            self._selected_sub_identity = None
        self.on_generate()

    def on_new(self):
        self.spot_combo.set(SPOTS[0])
        self.p1_pos.set("BTN")
        self.p2_pos.set("SB")
        self.p3_pos.set("BB")
        self.p2_tipo.set("fish")
        self.p3_tipo.set("fish")

        for w in (
            self.p1_bet_min, self.p1_bet_max,
            self.p2_bet_min, self.p2_bet_max,
            self.p3_bet_min, self.p3_bet_max,
            self.p1_stack_min, self.p1_stack_max,
            self.p2_stack_min, self.p2_stack_max,
            self.p3_stack_min, self.p3_stack_max,
            self.p1_se_min, self.p1_se_max,
        ):
            self._set_entry(w, "0.0")

        for w in (
            self.p1_bet_max, self.p2_bet_max, self.p3_bet_max,
            self.p1_stack_max, self.p2_stack_max, self.p3_stack_max,
            self.p1_se_max,
        ):
            self._set_entry(w, "75.0")

        self.or_panel.reset()
        self.or_panel.hide()

        self.current_sub_index = None
        self.sub_list.selection_clear(0, "end")
        self.on_generate()

    def on_copy(self):
        payload = self.build_payload()
        j = json.dumps(payload, indent=2, ensure_ascii=False)
        self.clipboard_clear()
        self.clipboard_append(j)
        messagebox.showinfo("Copiado", "JSON copiado al portapapeles.")

    @staticmethod
    def _set_entry(entry, value):
        entry.delete(0, "end")
        entry.insert(0, str(value))


