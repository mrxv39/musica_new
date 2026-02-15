# Wiki Técnica — musica_new (v0.5.2)

## 🧱 Arquitectura General

musica_new está dividido en tres capas claramente separadas:

1️⃣ Vision Layer (Pipeline determinista)  
2️⃣ UI Estrategias (editor de subestrategias)  
3️⃣ Engine de decisión (encontrar_move.py)

---

# 1️⃣ Vision Layer

Entrada:
- Imagen estática desde carpeta `/preflop`

Salida (dict estructurado):

{
  mano: "3c8h",
  dealer: "p1",
  stackefectivo: float,
  p1bet, p2bet, p3bet,
  p1stack, p2stack, p3stack,
  p2tipo, p3tipo
}

Características:

- Sin estado persistente
- Determinista
- No depende de servidor
- OCR estabilizado
- main.py convierte cartas reales → notación estándar (83o)

---

# 🂡 Representación de manos

Pipeline detecta cartas reales:
    3c8h

Se normaliza a notación de rango:
    83o
    KQs
    TT
    AA

Reglas:
- Orden descendente
- s = suited
- o = offsuit
- pares = AA

---

# 2️⃣ UI Estrategias

Ejecutable:

    python -m ui

Permite crear subestrategias agrupadas por:

    estrategia_global

Cada subestrategia contiene:

## Identificación

- spot
- p1_position
- p2_position
- p3_position
- situacion

## Filtros numéricos

- p1_bet_min / max
- p1_stack_min / max
- p1_stackef_min / max
- p2_stack_min / max
- p3_stack_min / max

## Tipo de jugador

- fish
- fish_pasivo
- fish_agresivo
- reg
- reg_pasivo
- reg_agresivo

## Bloques de movimiento

Cada subestrategia puede definir:

- open_push
- or_to_push
- or_to_call_small
- or_to_fold

Cada bloque contiene:

{
  rango estilo FlopZilla,
  move: OR / PUSH / FOLD,
  value_min,
  value_max
}

Persistencia:

    ui/estrategias_store.json

---

# 3️⃣ Engine de decisión (encontrar_move.py)

Flujo:

1. main.py ejecuta pipeline
2. build_state_from_pipeline()
3. encontrar_move(state)

Proceso interno:

1️⃣ Buscar subestrategia compatible
   - match por spot
   - posiciones
   - tipos
   - rangos numéricos

2️⃣ Selección de bloque

   PRIORIDAD:
   - Primero se comprueba si la mano pertenece al rango del bloque
   - Si coincide → ese bloque es seleccionado
   - Si no coincide ningún bloque → fallback a or_to_fold (si existe)

3️⃣ Devuelve:

{
  block,
  move,
  value_min,
  value_max,
  matched_by: "mano"
}

---

# 📂 Estructura actual

musica_new/
│
├── main.py
├── encontrar_move.py
├── preflop/
│
├── ui/
│   ├── app.py
│   ├── widgets.py
│   ├── store.py
│   ├── utils.py
│   ├── constants.py
│   └── estrategias_store.json
│
└── docs/
    ├── wiki_tecnica.md
    ├── wiki_usuario.md
    ├── hoja_de_ruta.txt
    └── changelog.md

---

Estado técnico: estable v0.5.2  
Engine basado en pertenencia de mano a rango.

## v0.5.1 — Selección por mano y fallback
- El engine elige bloque por pertenencia de mano a listas *_hands (con normalización).
- Si no hay match de mano -> fallback duro: FOLD, value_min=0.0, value_max=0.0.

---

## Sub-strategy Identity Logic

A sub-strategy identity is defined by:

- spot
- situacion
- hero position
- p2 position
- p3 position
- p2 type
- p3 type
- effective stack range (min/max)

If these fields change, UI prompts:

Yes → update existing
No → create new
Cancel → abort save

This prevents silent duplication while keeping flexibility.

---

# Range System (Refactor)

## Nuevo comportamiento UI

Cada fila de rango (OR_TO_PUSH, OR_TO_FOLD, OPEN_PUSH, etc):

- Guarda internamente el rango real como string.
- Muestra solo el contador de manos en la UI.
- El rango completo se edita en popup estilo FlopZilla.

Esto evita:
- Desbordamiento visual.
- Layout roto.
- Ruido visual innecesario.

## Nash Integration

Se añadió:

tools/make_btn_0_6_store.py

Este script:
- Lee chart engine/charts/nash_btn_3h_maxbb.json
- Genera estrategia BASE
- Inserta subestrategia BTNvsSB_BB_FISH_FISH_0_6

Diseño:
UI principal = editor estratégico
Nash Editor = herramienta auxiliar independiente

