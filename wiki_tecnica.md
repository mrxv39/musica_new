# Wiki Técnica – musica_new

## Arquitectura

Proyecto basado en detección por template matching y análisis directo de imagen.

### Estructura actual

- main.py
- reconocer_mano.py
- encontrar_time.py
- encontrar_noboard.py
- preflop/
  - templates/
  - crops/

---

## reconocer_mano.py

Funcionalidad:
- Carga imagen más reciente de preflop/
- Recorta regiones:
  - region_carta1
  - region_carta2
- Guarda crops en preflop/crops
- Busca templates en:
  - cartasc
  - cartasd
  - cartash
  - cartass
- Usa cv2.matchTemplate (TM_CCOEFF_NORMED)

Observaciones:
- Template matching directo sin resize.
- Score comparativo entre suits.
- Rank detection confirmada por diferencia relativa de scores.

---

## encontrar_time.py

- ROI fija.
- Búsqueda de time.bmp con matchTemplate.
- Threshold alto (0.85) por estabilidad del elemento.

---

## encontrar_noboard.py

NO usa template matching.

Motivo:
- no_board.png es una imagen plana (negra).
- TM_CCOEFF_NORMED es inválido para templates sin varianza.

Método actual:
- Análisis estadístico de ROI:
  - mean (intensidad media)
  - std (desviación estándar)
  - dark_ratio (% píxeles oscuros)
- Clasificación como NOBOARD si:
  - mean bajo
  - std bajo
  - dark_ratio alto

---

## Decisiones de diseño

- Cada detector es independiente.
- No hay aún orquestador central de estados.
- Prioridad en simplicidad y determinismo.
