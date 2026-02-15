# Changelog — musica_new

## v0.5.0 — Engine por mano

- Motor ahora selecciona bloque por pertenencia de mano al rango.
- Conversión automática de cartas reales (3c8h → 83o).
- Eliminado wrapper inestable de pipeline.
- Reestructuración limpia de main.py.
- Report simplificado.
- Expansión básica de rangos estilo FlopZilla:
    - AA-99
    - AKO-ATO
    - A9S-A2S
    - etc.

Estado: estable.

2026-02-15 — Engine: selección por mano + fallback duro

ANTES:
- El engine podía devolver Move: (none) si no coincidía ningún bloque por value o si faltaba mano en state.

AHORA:
- El engine selecciona bloque por pertenencia de mano a *_hands (normaliza 83O/83o).
- Si no hay match de mano en ningún bloque -> FOLD con value_min=0.0 y value_max=0.0.

IMPACTO:
- Decisiones deterministas por mano y sin estados "none".

