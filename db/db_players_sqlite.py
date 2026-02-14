# db/db_players_sqlite.py
from __future__ import annotations

import sqlite3
from typing import Optional, Tuple

DB_PATH_DEFAULT = "players.db"

TIPOS_VALIDOS = {
    "fish",
    "fish_pasibo",
    "fish_agresivo",
    "reg",
    "reg_pasibo",
    "reg_agresibo",
}


def _norm(s: str) -> str:
    return (s or "").strip()


def _connect(db_path: str) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    # WAL ayuda si luego tienes varios procesos leyendo/escribiendo
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con


def ensure_schema(db_path: str = DB_PATH_DEFAULT) -> None:
    con = _connect(db_path)
    try:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS jugadores (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          sala TEXT NOT NULL,
          name TEXT NOT NULL,
          tipo TEXT NOT NULL DEFAULT 'fish',
          created_at TEXT NOT NULL DEFAULT (datetime('now')),
          updated_at TEXT NOT NULL DEFAULT (datetime('now')),
          UNIQUE(sala, name)
        );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_jugadores_sala_name ON jugadores(sala, name);")
        con.commit()
    finally:
        con.close()


def get_or_create_tipo(sala: str, name: str, db_path: str = DB_PATH_DEFAULT, default_tipo: str = "fish") -> str:
    sala_n = _norm(sala)
    name_n = _norm(name)

    if not sala_n or not name_n:
        return "fish"

    default = default_tipo if default_tipo in TIPOS_VALIDOS else "fish"

    ensure_schema(db_path)

    con = _connect(db_path)
    try:
        cur = con.cursor()
        cur.execute("SELECT tipo FROM jugadores WHERE sala=? AND name=? LIMIT 1", (sala_n, name_n))
        row = cur.fetchone()
        if row and row[0]:
            t = _norm(row[0])
            return t if t in TIPOS_VALIDOS else "fish"

        cur.execute(
            "INSERT OR IGNORE INTO jugadores (sala, name, tipo) VALUES (?, ?, ?)",
            (sala_n, name_n, default),
        )
        con.commit()
        return default
    finally:
        con.close()


def set_tipo(sala: str, name: str, tipo: str, db_path: str = DB_PATH_DEFAULT) -> bool:
    sala_n = _norm(sala)
    name_n = _norm(name)
    tipo_n = _norm(tipo)

    if not sala_n or not name_n:
        return False
    if tipo_n not in TIPOS_VALIDOS:
        return False

    ensure_schema(db_path)

    con = _connect(db_path)
    try:
        cur = con.cursor()
        # asegura existencia
        cur.execute(
            "INSERT OR IGNORE INTO jugadores (sala, name, tipo) VALUES (?, ?, 'fish')",
            (sala_n, name_n),
        )
        cur.execute(
            "UPDATE jugadores SET tipo=?, updated_at=datetime('now') WHERE sala=? AND name=?",
            (tipo_n, sala_n, name_n),
        )
        con.commit()
        return cur.rowcount > 0
    finally:
        con.close()
