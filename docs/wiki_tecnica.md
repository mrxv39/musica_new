
# Wiki técnica – musica_new

## Arquitectura

Sistema modular basado en detección por imagen estática dentro de la carpeta preflop/.
Uso de OpenCV (cv2.matchTemplate) con ROIs fijas.
Sin base de datos activa.
Sin realtime.

## Módulos / carpetas

- main.py → Orquestador principal.
- reconocer_mano.py → Detección de rank y suit.
- encontrar_time.py → Detección de botón TIME.
- encontrar_noboard.py → Detección estadística de mesa sin board.
- preflop/templates/ → Templates de cartas y time.
- preflop/crops/ → Crops temporales para debug.

## Funcionalidades implementadas

- Detección de cartas (rank + suit).
- Detección TIME.
- Detección NOBOARD.
- Salida limpia estructurada:
	mano: <valor>
	time: <True/False>
	noboard: <True/False>

## Decisiones técnicas relevantes

- Uso de TM_CCOEFF_NORMED.
- Threshold rank/suit: 0.60.
- Threshold TIME: 0.85.
- NOBOARD basado en mean/std/dark_ratio.
- ROIs fijas calibradas manualmente.
- Los módulos devuelven valores y no imprimen debug.