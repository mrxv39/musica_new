# ui/constants.py

POSITIONS = ["BTN", "SB", "BB"]

# Estrategias globales (agrupan subestrategias)
ESTRATEGIAS_GLOBALES = [
    "BASE",
    "BTN_vs_BB_SB__DEFAULT",
    "SB_vs_BTN_BB__DEFAULT",
    "BB_vs_BTN_SB__DEFAULT",
]

# Selector "spot" en Crear estrategia (con filtrado)
SPOTS = [
    "BTN",
    "SBvsBTN",
    "SBvsBB_3H",
    "BBvsBTN",
    "BBvsSB_3H",
]

STACK_MIN = 0.0
STACK_MAX = 75.0

STORE_FILENAME = "estrategias_store.json"
