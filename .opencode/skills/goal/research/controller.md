# research-controller.md — FASE 1.R Auto-research (complemento de SKILL.md)

> **No expande SKILL.md.** Este archivo es el controlador externo referenciado por FASE 1.R. Si `research.enabled=false`, coste 0.

## Activación (2 vías)

1. **Explícita (humano):** `/goal "mejorar $/K churn en X" --research` o `research: {metric, target, harness}` en `PLAN.md`
2. **Autónoma (agente):** en FASE -1 el agente puede proponer `research.enabled=true` si detecta: métrica cuantificable + harness determinista posible + mejora estimada > `epsilon`. Debe preguntar en `grill me` (1 línea: "¿Activo auto-research para <métrica>?") salvo que el objetivo ya diga "optimiza/mejora + métrica". Nunca activar en TRIVIAL.

## Pre-condición FASE 0b — Deep research inicial

Antes del loop 1.R, ejecuta **Deep research de arranque** (igual que FASE 1b.2 pero proactivo): `websearch` + `Context7` sobre la temática/métrica, 3-7 bullets con fuente en `LOG.md ## RESEARCH-INIT`. Luego comité de arranque mínimo (1 juez) valida hipótesis iniciales. Si `sin research útil`, sigue sin 1.R.

## Estructura hallable (2 reads)

```
.opencode/goals/<slug>/research/
  INDEX.md                          <- READ 1: tabla machine-readable
  2026-10-18_vec-bm25-hnsw/
    NOTE.md                         <- READ 2
    artifacts/ (opcional)
```

- **Carpeta:** `YYYY-MM-DD_<investigacion-kebab>__delta<signo><valor>/` — protocolo `fecha - investigación - mejora`. Fecha = orden lexicográfico, investigación = slug estable, mejora = delta del ciclo (ej: `m08` = -8.1%, `p03` = +3%). Sin `HHMM`, sin `auto/` (YAGNI). Si algún día coexiste `manual/`, se migra a `research/auto/` + `research/manual/` y se filtra por campo `type`.

  Ejemplos:
  - `2026-10-18_gate-calificado__m08/` (gate = -8.1%)
  - `2026-10-18_coalescing-batch__m05/` (coalescing = -4.9% adicional)
  - `2026-10-18_holdout-live__m02/` (holdout = -2.1% degradación validada)
- **INDEX.md** (append-only, fuente de verdad para early-stop):
```md
# Research Index — <slug>
early_stop: 2
| fecha | slug | type | verdict | consecutive_fails | link |
| 2026-10-18 | vec-bm25-hnsw | auto | fail | 1 | ./2026-10-18_vec-bm25-hnsw/NOTE.md |
```
- **NOTE.md** por experimento (con frontmatter `verdict: fail/success`):
```
---
verdict: fail
metric_value: 0.21
delta: -0.02
---
## Hipótesis
## Protocolo
## Evidencia
## Veredicto
```

## Loop 1.R — determinista y acotado

- **Presupuesto:** max 5 ciclos, cada ciclo = 1 iter del límite global de 15 (no presupuesto paralelo). `INDEX.md: early_stop: 2` → si `consecutive_fails >=2`, para y evalúa comité.
- **Harness frozen:** definido en FASE 0b con `harness` + `harness_hash: sha256:...` (ej: `DATE=2026-01-01 node:22`). Misma hipótesis con mismo hash → mismo resultado.
- **Un ciclo:** hipótesis falsable → parche mínimo → `harness` → `result.json` `{metric_value, delta}` → escribe `NOTE.md` + actualiza `INDEX.md`.
- **Promoción a steps/:** solo si `delta` supera `target` y **replica 2 mediciones** con mismo `harness_hash` + pasa `tests no mentirosos`. Si no, queda en sandbox y se descarta.

## Memoria

- **Detallada:** `research/INDEX.md` + `research/*/NOTE.md` (append-only, nunca se borra).
- **Resumida:** 1 línea agregada a `CONTEXT.md` FIFO (`research: mejor delta <hash>`) + 1 línea en `LOG.md` + 1 línea en `INDEX.md` global apuntando a `research/INDEX.md`.
- **Descubrimiento:** `read research/INDEX.md` (READ 1) → sabes si parar y qué experimento abrir → `read research/YYYY-MM-DD_slug/NOTE.md` (READ 2).

## Límites y comité

- Loop normal no invoca comité. Solo si `early_stop` dispara tras 2 fallos → invoca **FASE 1b comité (consume 1 de los 6 globales)** con `## RESEARCH` acumulado como contexto. Tras veredicto, vuelve a 1.R o cierra research.
- **Trigger mini-skill por comité:** si FASE 1b resuelve un bloqueo (2 fallos → comité → fix), propone candidata mini-skill anti-patrones en `research/YYYY-MM-DD_<slug>__mXX/NOTE.md` con lección; promoción solo si pasa tests no mentirosos + replica x2 + auditor PASS (ver `mini-skills/README.md`).
- Techo global sigue siendo 15 iter / 6 comités. Research nunca lo expande.
