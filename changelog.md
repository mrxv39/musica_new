# Changelog – musica_new

## [0.1.0] - 2026-02-13

### Añadido
- main.py como punto de entrada principal.
- reconocer_mano.py:
  - Recorte de regiones carta1 y carta2.
  - Guardado automático de crops en preflop/crops.
  - Template matching simple usando cv2.matchTemplate.
  - Debug de scores por rank (incluyendo verificación 3c/3d/3h/3s).
- encontrar_time.py:
  - Recorte ROI fija.
  - Detección de time.bmp dentro de ROI.
- encontrar_noboard.py:
  - Recorte ROI (120,200,200,200).
  - Detección NOBOARD por análisis de intensidad (zona negra uniforme).
  - Eliminado uso de matchTemplate para template plano.

### Estado actual
- Reconocimiento de rank funcional.
- Detección de TIME funcional.
- Detección de NOBOARD funcional mediante análisis estadístico.
- Arquitectura modular por detectores independientes.

### Pendiente
- Separar detección de rank y suit.
- Integración de todos los detectores en pipeline único.
- Control de estados (TIME, NOBOARD, DEALER, etc.).
