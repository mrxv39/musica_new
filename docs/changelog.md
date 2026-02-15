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

# Changelog

## v0.5.2

### UI
- Added update vs create-new popup when editing key fields
- Prevent infinite chain of sub-strategy creation
- Preserve sub_id when updating existing strategy
- Introduced _sub_identity() to define identity fields

### Engine
- Hand-based matching stable
- Hard fallback guaranteed
- Case-insensitive suitedness matching

### Store
- UI store is now source of truth
- Tests adapted to follow real store content


## [UI Range Refactor + Nash Integration]

### Added
- Script tools/make_btn_0_6_store.py para generar estrategia BASE desde chart Nash.
- Soporte para contador de manos en filas OR / OPEN.
- Integración inicial de Nash Editor externo.

### Changed
- Las filas de rango ya no muestran el listado completo de manos.
- Ahora muestran solo: "X manos".
- El rango completo se edita vía popup.
- Mejorado layout para evitar overflow horizontal.

### Fixed
- Problemas de indentación en or_ranges.py.
- Errores al cargar payload con listas en lugar de string.
- Desbordamiento visual de rangos largos.

