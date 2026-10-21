---
name: goal-research
description: "Activa GOAL con auto-research para bajar métrica (harness+delta). Usa /goal-research"
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "false"
  opencode/autoinvoke: "false"
---

# /goal-research — GOAL con auto-research

Wrapper que activa `research.enabled=true` y delega a `goal`.

**Uso:** `/goal-research "bajar latencia p95 de X a <Yms" --metric="p95" --target="-10%"`

Equivale a `/goal "objetivo" --research --metric="..." --target="..."`

Flujo: deep research inicial (3-7 bullets) → loop 1.R max 5 ciclos con `harness_hash` → early_stop 2 fallos → promoción solo si delta replica x2 + tests no mentirosos. Ver `research/controller.md`.

Sin métrica cuantificable o en TRIVIAL, no activa research y avisa.
