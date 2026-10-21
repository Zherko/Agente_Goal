---
name: goal-plan
description: "Particiona un objetivo en 3-7 pasos ejecutables con agente plan (read-only). Usalo desde Goal FASE 0b cuando no hay plan valido."
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "false"
  opencode/autoinvoke: "false"
---

## Objetivo
Diseña la partición sin modificar código (edit: deny / bash: deny). Enjambre-aware pero sin forzar.

## Flujo
1. Lee código (read/grep/glob) + `ENJAMBRE-RULES.md` + `block.schema.json` y propone partición 3-7 pasos con dependencias. Escribe en `LOG.md` `## PLAN — <objetivo>` la propuesta. Aplica Regla 0 (TRIVIAL/SMALL → no paralelizar; solo LARGE >10k tok o 3+ docs disjuntos) y Regla 1 (solo `paralelizable? SÍ` si interfaces estables + archivos disjuntos + I/O-bound). Si no compensa, `NO` + 1 línea por qué. **Robust-first por coste:** `alto` → harness seed 42 + contrato previo; `medio/bajo` → check ligero 5 líneas.
2. Materializa `PLAN.md` (Objetivo, Éxito verificable 3-7 criterios, Pasos tabla N|nombre|archivos|depende-de|paralelizable?|verificar, Riesgos, Estado) y `steps/NN-*.md` por paso. Si algún paso es `SÍ`, bosqueja `block.json` con claims. La columna `paralelizable?` es hipótesis no vinculante; el runtime la verifica y degrada a secuencial si hay solape.

## Auto-research opcional
Si `research.enabled=true`, define `research: {metric, target, harness, harness_hash}` en PLAN.md e inicializa `research/INDEX.md` con `early_stop: 2`.
