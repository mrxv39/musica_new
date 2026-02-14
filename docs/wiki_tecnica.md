# Wiki Técnica — musica_new

## Arquitectura General

Proyecto modular basado en detección por imagen estática.

Directorio principal:

preflop/
 ├── templates/
 ├── crops/
 └── screenshot_*.bmp

main.py orquesta los módulos.

---

## Módulos Actuales

### reconocer_mano.py
- Template matching TM_CCOEFF_NORMED
- Threshold: 0.60
- Detecta rank y suit
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
- ROI = imagen completa
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

## Convenciones

- Todos los módulos exponen run_quiet()
- Sin prints
- Devuelven tipos puros
- Debug activable por variable entorno OCR_DEBUG_*

---

## Estado del Pipeline

El pipeline es determinista.
No depende de estado previo.
No usa base de datos.
No es realtime aún.
