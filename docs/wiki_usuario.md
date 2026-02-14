# Wiki Usuario — musica_new

## ¿Qué hace el sistema?

Analiza una captura de mesa de poker (preflop) y devuelve:

- Mano del héroe
- Si es su turno
- Si no hay board
- Dealer
- Stack efectivo
- Apuestas actuales
- Stacks individuales

---

## Cómo ejecutar

Colocar screenshot en carpeta:

preflop/

Ejecutar:

python main.py

Salida:

--- RESULT ---
mano: 3c8h
time: True
noboard: True
dealer: p1
stackefectivo: 25.0
p1bet: 0.0
p2bet: 0.5
p3bet: 1.0
p1stack: 25.0
p2stack: 24.5
p3stack: 24.0

---

## Debug

Activar guardado de crops:

$env:OCR_DEBUG_BETS="1"
$env:OCR_DEBUG_STACKS="1"

Los crops se guardan en:

preflop/crops/
