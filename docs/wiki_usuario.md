# Wiki Usuario — musica_new

## ¿Qué hace el sistema?

Tiene 2 partes:

1) **Detector preflop**: analiza una captura y devuelve mano/estado (time, noboard, dealer, stacks, bets, stack efectivo).  
2) **UI de estrategias**: permite crear y guardar subestrategias con rangos (bet/stack) y campos extra.

---

## Cómo ejecutar el detector preflop

1) Coloca un screenshot en:
- `preflop/`

2) Ejecuta:
- `python main.py`

Salida (ejemplo):
- mano: 3c8h
- time: True
- noboard: True
- dealer: p1
- stackefectivo: 25.0
- p1bet/p2bet/p3bet
- p1stack/p2stack/p3stack

---

## Cómo abrir la UI de estrategias

Ejecuta:
- `python -m ui`

---

## Crear una subestrategia (UI)

1) Selecciona el **spot** (puedes escribir para filtrar).
2) Completa los campos:

### HERO
- position
- bet min / bet max (0.0–75.0)
- stack min / stack max (0.0–75.0)
- stack efectivo min / max (0.0–75.0)

### P2 y P3
- position
- tipo
- bet min / bet max (0.0–75.0)
- stack min / stack max (0.0–75.0)

3) Pulsa **Generar** para ver el JSON.
4) Pulsa **Guardar subestrategia** para guardarla en la estrategia global actual.
5) En la barra lateral, al seleccionar una subestrategia, se cargan sus valores.

---

## Copiar y borrar

- **Copiar JSON**: copia el payload al portapapeles.
- **Borrar subestrategia**: elimina la seleccionada.
- **Refrescar**: vuelve a cargar la lista.

---

## Debug (detector preflop)

Ejemplos:
- `$env:OCR_DEBUG_BETS="1"`
- `$env:OCR_DEBUG_STACKS="1"`

Crops:
- `preflop/crops/`
