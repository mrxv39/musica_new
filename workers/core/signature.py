# workers/core/signature.py

from __future__ import annotations

import json


def build_signature(mesa: int, data: dict) -> str:
    return json.dumps(
        {
            "mesa": mesa,
            "mano": data.get("mano"),
            "move": data.get("move"),
            "block": data.get("block"),
            "p2bet": data.get("p2bet"),
            "p3bet": data.get("p3bet"),
            "stackefectivo": data.get("stackefectivo"),
        },
        sort_keys=True,
        ensure_ascii=False,
    )


def is_duplicate(sig: str, last_sig: str) -> bool:
    return sig == last_sig
