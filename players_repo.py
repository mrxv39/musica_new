# players_repo.py
from __future__ import annotations

import os
from typing import Optional

from db.db_players_sqlite import get_or_create_tipo as _sqlite_get_or_create_tipo
from db.db_players_sqlite import set_tipo as _sqlite_set_tipo

# Para migrar a Postgres en el futuro:
# - creas db/db_players_postgres.py con la MISMA interfaz
# - y cambias aquí el "backend" por env var (sin tocar el pipeline)

DEFAULT_SALA = "champion_poker"


def _db_path() -> str:
    return os.getenv("PLAYERS_DB_PATH", "data/players.db")


def get_or_create_player_tipo(name: str, sala: str = DEFAULT_SALA) -> str:
    return _sqlite_get_or_create_tipo(sala=sala, name=name, db_path=_db_path(), default_tipo="fish")


def set_player_tipo(name: str, tipo: str, sala: str = DEFAULT_SALA) -> bool:
    return _sqlite_set_tipo(sala=sala, name=name, tipo=tipo, db_path=_db_path())
