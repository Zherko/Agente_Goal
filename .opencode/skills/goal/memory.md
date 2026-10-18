---
updated: 2026-10-18
version: 2
limit: 2200  # chars ~800 tokens, estilo Hermes MEMORY.md (antes 100 líneas)
limit_user: 1375  # para USER.md si se separa
mode: hard  # límite duro: error si se excede, obliga consolidar en batch
---

# Goal — Memoria usuario (curada, límite duro estilo Hermes)
# Reglas: límite 2.200 chars. Si un add/patch excede, la tool devuelve error con current_entries y exige batch que libere espacio (remove/patch) + add en la misma operación. No hay FIFO silencioso. Ver memory/README.md

## Preferencias (max 35)
- [2026-10-17] respuestas breves 1-5 líneas, 1 tecnicismo max; `detalla` rompe límite

## Hechos (max 35)
- [2026-10-17] agente Goal global: skills/goal + agents/goal + comando /skill_goal
- [2026-10-17] GO plan activo, Jev descartado (fuera de GO)

## Anti-patrones (max 20)
- [2026-10-17] no usar Jev ni Console fuera de GO
- [2026-10-17] no auto-inyectar memoria completa en CONTEXT.md

## Pendientes (max 10)
- [2026-10-17] definir hook compact cada 5 ciclos
