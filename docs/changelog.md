# Changelog — musica_new

## 2026-02-14 — UI Estrategias (Tkinter)

ANTES:
- Solo pipeline preflop por imagen estática, sin UI de estrategias.

AHORA:
- UI modular para crear/gestionar estrategias y subestrategias por “estrategia global”.
- Inputs con rangos seleccionables:
  - bet_min/bet_max (0.0–75.0) para HERO/P2/P3
  - stack_min/stack_max (0.0–75.0) para HERO/P2/P3
  - stack_efectivo (solo HERO): stackef_min/stackef_max (0.0–75.0)
- Campo “tipo” en P2 y P3 (select).
- Campo “spot” con combobox filtrable.
- Sidebar: selector de estrategia global + lista de subestrategias (cargar/borrar/refrescar).
- Salida JSON visible + copiar al portapapeles.

IMPACTO:
- Se puede construir una librería de subestrategias consistente, reutilizable y editable sin tocar código.

---

## 51163bc
feat: add stacks OCR and include p1/p2/p3 stacks in main result

## ff247f8
feat: add stackefectivo OCR and include it in main result

## c1f1c72
feat: add dealer detection module

## e0c81d9
fix: main result reflects actual detections

## Proyecto actual
Pipeline preflop modular y estable. Detectores funcionan correctamente.
