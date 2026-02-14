# ui/store.py

from __future__ import annotations

import json
import os
from typing import Any

from .constants import STORE_FILENAME


def store_path() -> str:
    return os.path.join(os.path.dirname(__file__), STORE_FILENAME)


def load_store() -> dict:
    path = store_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_store(store: dict) -> None:
    path = store_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


def ensure_global(store: dict, global_name: str) -> None:
    if global_name not in store:
        store[global_name] = []


def list_subs(store: dict, global_name: str) -> list[dict]:
    items = store.get(global_name, [])
    return items if isinstance(items, list) else []


def upsert_sub(store: dict, global_name: str, sub_id: str, payload: dict) -> int:
    ensure_global(store, global_name)
    items = store[global_name]
    for i, it in enumerate(items):
        if it.get("id") == sub_id:
            it["payload"] = payload
            return i
    items.append({"id": sub_id, "payload": payload})
    return len(items) - 1


def delete_sub(store: dict, global_name: str, index: int) -> None:
    items = list_subs(store, global_name)
    if 0 <= index < len(items):
        items.pop(index)
        store[global_name] = items
