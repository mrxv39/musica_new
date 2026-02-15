import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHART_PATH = os.path.join(ROOT, "engine", "charts", "nash_btn_3h_maxbb.json")

def load_chart():
    if not os.path.exists(CHART_PATH):
        return {"_meta": {}}
    with open(CHART_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    if not isinstance(d, dict):
        d = {"_meta": {}}
    d.setdefault("_meta", {})
    return d

def save_chart(d):
    with open(CHART_PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

class NashEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nash Editor (BTN 3H)")
        self.geometry("900x600")

        self.data = load_chart()
        self.hands = sorted([k for k in self.data.keys() if k != "_meta"])

        self.hand_var = tk.StringVar()
        self.min_var = tk.StringVar()
        self.max_var = tk.StringVar()
        self.fold_var = tk.BooleanVar()

        self._build()
        self._load_first()

    def _build(self):
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)

        self.listbox = tk.Listbox(left, width=12)
        self.listbox.pack(fill="y", expand=True)
        for h in self.hands:
            self.listbox.insert(tk.END, h)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ttk.Label(right, text="Hand").pack(anchor="w")
        ttk.Entry(right, textvariable=self.hand_var, state="readonly").pack(anchor="w")

        ttk.Checkbutton(right, text="FOLD", variable=self.fold_var).pack(anchor="w", pady=10)

        ttk.Label(right, text="min bb").pack(anchor="w")
        ttk.Entry(right, textvariable=self.min_var).pack(anchor="w")

        ttk.Label(right, text="max bb").pack(anchor="w")
        ttk.Entry(right, textvariable=self.max_var).pack(anchor="w")

        ttk.Button(right, text="Apply", command=self._apply).pack(anchor="e", pady=20)
        ttk.Button(right, text="Save JSON", command=self._save).pack(anchor="e")

    def _load_first(self):
        if not self.hands:
            return
        self.listbox.selection_set(0)
        self._on_select()

    def _on_select(self, _evt=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        hand = self.listbox.get(sel[0])
        self.hand_var.set(hand)
        rule = self.data.get(hand)

        if rule is None:
            self.fold_var.set(True)
            self.min_var.set("")
            self.max_var.set("")
        elif isinstance(rule, list) and len(rule) == 2:
            self.fold_var.set(False)
            self.min_var.set(str(rule[0]))
            self.max_var.set(str(rule[1]))
        else:
            self.fold_var.set(False)
            self.min_var.set("0")
            self.max_var.set(str(rule))

    def _apply(self):
        hand = self.hand_var.get()
        if self.fold_var.get():
            self.data[hand] = None
        else:
            try:
                lo = float(self.min_var.get())
                hi = float(self.max_var.get())
            except:
                messagebox.showerror("Error","Invalid numbers")
                return
            self.data[hand] = [lo, hi]
        messagebox.showinfo("OK", f"{hand} updated")

    def _save(self):
        save_chart(self.data)
        messagebox.showinfo("Saved", "JSON updated")

if __name__ == "__main__":
    NashEditor().mainloop()
