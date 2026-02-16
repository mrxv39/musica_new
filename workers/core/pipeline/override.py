# C:\Users\Usuario\Desktop\projectos\musica_new\workers\core\pipeline\override.py

from __future__ import annotations

from workers.core.detectors import mano_valida


def override_mano_if_needed(mano_detectada: str, data: dict) -> bool:
    """
    FIX quirúrgico:
    - Si main devuelve mano vacía/NN
    - pero el worker detectó una mano válida
    => imponemos la mano del worker para el INSERT
    """
    if not mano_valida(mano_detectada):
        return False

    mano_main = (data.get("mano") or "").strip()
    if mano_valida(mano_main):
        return False

    data["mano"] = mano_detectada
    if not data.get("mano_raw"):
        data["mano_raw"] = mano_detectada
    data["mano_source"] = "worker_override"
    return True
