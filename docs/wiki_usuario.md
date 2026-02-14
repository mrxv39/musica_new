# Wiki Usuario — musica_new (v0.5.0)

## 🎯 Objetivo

Sistema automático de reconocimiento de mano y selección de movimiento preflop basado en estrategias configurables.

---

# 🖥 Paso 1 — Crear Estrategias

Ejecutar:

    python -m ui

En la interfaz:

1. Crear subestrategia
2. Definir:
   - spot
   - posiciones
   - tipos de rival
   - rangos de stack y bet

3. Definir bloques:

   OR_TO_PUSH
   OR_TO_CALL_SMALL
   OR_TO_FOLD
   OPEN_PUSH

Cada bloque permite:

- Pegar rango estilo FlopZilla:
    AA-99
    AKO-ATO
    A9S-A2S
- Seleccionar move
- Definir value_min y value_max

Guardar.

---

# 🖥 Paso 2 — Ejecutar motor

    python main.py

Salida ejemplo:

--- REPORT ---

HERO position: BTN  
MANO: 83o  
stackefectivo: 25.0  

P2  
  position: SB  
  stack: 24.5  
  bet: 0.5  
  tipo: fish  

P3  
  position: BB  
  stack: 24.0  
  bet: 1.0  
  tipo: fish  

MOVE  
  Subestrategia: BTN__BTN_vs_BB_SB__...  
  Move: FOLD  

---

# 🧠 Cómo decide el sistema

1️⃣ Busca subestrategia compatible  
2️⃣ Comprueba si la mano pertenece a algún rango  
3️⃣ Si pertenece → selecciona ese bloque  
4️⃣ Si no pertenece → usa OR_TO_FOLD si existe  

La decisión no depende únicamente del value actual.  
La mano tiene prioridad.

---

# 📌 Versionado

Versión actual: v0.5.0  
Motor basado en rangos por mano.
