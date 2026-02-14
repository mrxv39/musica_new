# Wiki Técnica — musica_new

## Arquitectura General

Proyecto modular con 2 capas principales:

1) **Vision / OCR (pipeline preflop)**  
Basado en detección por imagen estática (`preflop/`) y módulos puros (sin prints).

2) **UI Estrategias (Tkinter)**  
Permite crear/gestionar estrategias y subestrategias con inputs normalizados (rangos).

---

## Estructura de carpetas (alto nivel)

- `preflop/`
  - `templates/`
  - `crops/`
  - `screenshot_*.bmp`
- `ui/`
  - `app.py` (ventana principal)
  - `widgets.py` (constructores de widgets reutilizables)
  - `store.py` (persistencia de subestrategias)
  - `utils.py` (helpers: safe_float, ids, situacion)
  - `constants.py` (listas: POSITIONS, SPOTS, etc.)
  - `__main__.py` (python -m ui)

---

## Pipeline preflop (Vision/OCR)

`main.py` orquesta módulos.

### reconocer_mano.py
- Template matching TM_CCOEFF_NORMED
- Threshold: 0.60
- Devuelve string tipo "3c8h"

### encontrar_time.py
- ROI fija
- matchTemplate contra time.bmp
- Threshold 0.85

### encontrar_noboard.py
- Método estadístico
- mean ≤ 35
- std ≤ 18
- dark_ratio ≥ 0.85

### encontrar_dealer.py
- matchTemplate dealer.png
- Asignación por proximidad a anclas:
  - top-left → p2
  - top-right → p3
  - bottom-center → p1

### encontrar_stackefectivo.py
- OCR Tesseract
- Heurística decimal
- run_quiet()

### encontrar_bets.py
- OCR con upscale x3
- Doble binarización
- Heurística punto decimal
- Devuelve p1bet/p2bet/p3bet

### encontrar_stacks.py
- OCR con Otsu + fallback
- Heurística decimal (245 → 24.5)
- Devuelve p1stack/p2stack/p3stack

---

## Convenciones del pipeline

- Todos los módulos exponen `run_quiet()`
- Sin prints
- Devuelven tipos puros
- Debug activable por variables entorno `OCR_DEBUG_*`

---

## UI Estrategias (Tkinter)

### Objetivo
Construir una librería de subestrategias por “estrategia global” y visualizar el payload JSON.

### Componentes principales
- **Spot**: Combobox con filtrado (escritura + lista filtrada).
- **HERO (p1)**:
  - position
  - bet_min / bet_max (0.0–75.0)
  - stack_min / stack_max (0.0–75.0)
  - stack efectivo (solo hero): stackef_min / stackef_max (0.0–75.0)
- **P2 / P3**:
  - position
  - tipo (select)
  - bet_min / bet_max (0.0–75.0)
  - stack_min / stack_max (0.0–75.0)
- **Sidebar**:
  - selector de estrategia global
  - lista de subestrategias (select → carga en formulario)
  - borrar / refrescar
- **Salida**:
  - JSON generado (Text)
  - botón copiar JSON

### Validaciones
- Todos los rangos se normalizan:
  - clamp al intervalo [0.0, 75.0]
  - si min > max ⇒ max = min

### Persistencia (UI)
La UI guarda subestrategias mediante `ui/store.py` (estructura tipo “store” con upsert/delete/list).
El ID de subestrategia se deriva del payload (helper `make_sub_id`).

---

## Estado actual

- Pipeline preflop: estable, determinista, sin estado previo.
- UI estrategias: funcional, modular, con rangos y campos extra (stack efectivo hero + tipo villains).
