# workers/core/db.py

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def insert_hands_ocr(db_path: Path, mesa: int, data: dict) -> None:
    raw_pipeline = {
        "image_path": data.get("image_path"),
        "mano_raw": data.get("mano_raw"),
        "dealer": data.get("dealer"),
        "stackefectivo": data.get("stackefectivo"),
        "p1bet": data.get("p1bet"),
        "p2bet": data.get("p2bet"),
        "p3bet": data.get("p3bet"),
        "p1stack": data.get("p1stack"),
        "p2stack": data.get("p2stack"),
        "p3stack": data.get("p3stack"),
        "p2name": data.get("p2name"),
        "p3name": data.get("p3name"),
        "p2tipo": data.get("p2tipo"),
        "p3tipo": data.get("p3tipo"),
    }

    raw_state = {
        "estrategia_global": data.get("estrategia_global", "BASE"),
        "spot": data.get("spot", data.get("hero_position", "BTN")),
        "situacion": data.get("situacion"),
        "hero_position": data.get("hero_position", "BTN"),
        "mano": data.get("mano"),
        "dealer": data.get("dealer"),
        "stackefectivo": data.get("stackefectivo"),
        "p1bet": data.get("p1bet"),
        "p2bet": data.get("p2bet"),
        "p3bet": data.get("p3bet"),
        "p1stack": data.get("p1stack"),
        "p2stack": data.get("p2stack"),
        "p3stack": data.get("p3stack"),
        "p2tipo": data.get("p2tipo"),
        "p3tipo": data.get("p3tipo"),
    }

    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    cur.execute(
        """
        INSERT INTO hands_ocr (
            hand_id,
            mesa,
            image_path,
            estrategia_global,
            spot,
            situacion,
            hero_position,
            mano,
            dealer,
            stackefectivo,
            p1bet,
            p2bet,
            p3bet,
            p1stack,
            p2stack,
            p3stack,
            p2tipo,
            p3tipo,
            subestrategia_id,
            move,
            block,
            matched_by,
            value_min,
            value_max,
            raw_state_json,
            raw_pipeline_json
        ) VALUES (
            NULL,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """,
        (
            mesa,
            data.get("image_path"),
            data.get("estrategia_global", "BASE"),
            data.get("spot", data.get("hero_position", "BTN")),
            data.get("situacion"),
            data.get("hero_position", "BTN"),
            data.get("mano"),
            data.get("dealer"),
            data.get("stackefectivo"),
            data.get("p1bet"),
            data.get("p2bet"),
            data.get("p3bet"),
            data.get("p1stack"),
            data.get("p2stack"),
            data.get("p3stack"),
            data.get("p2tipo"),
            data.get("p3tipo"),
            data.get("sub_id"),
            data.get("move"),
            data.get("block"),
            data.get("matched_by"),
            data.get("value_min"),
            data.get("value_max"),
            json.dumps(raw_state, ensure_ascii=False),
            json.dumps(raw_pipeline, ensure_ascii=False),
        ),
    )

    con.commit()
    con.close()
