# research-controller.md — FASE 1.R Auto-research (complemento de SKILL.md)

> **No expande SKILL.md.** Este archivo es el controlador externo referenciado por FASE 1.R. Si `research.enabled=false`, coste 0.

## Activación (2 vías)

1. **Explícita (humano):** `/goal "mejorar $/K churn en X" --research` o `research: {metric, target, harness}` en `PLAN.md`
2. **Autónoma (agente):** en FASE -1 el agente puede proponer `research.enabled=true` si detecta: métrica cuantificable + harness determinista posible + mejora estimada > `epsilon`. Debe preguntar en `grill me` (1 línea: "¿Activo auto-research para <métrica>?") salvo que el objetivo ya diga "optimiza/mejora + métrica". Nunca activar en TRIVIAL.

## Pre-condición FASE 0b — Deep research inicial

Antes del loop 1.R, ejecuta **Deep research de arranque** (igual que FASE 1b.2 pero proactivo): `websearch` + `Context7` sobre la temática/métrica, 3-7 bullets con fuente en `LOG.md ## RESEARCH-INIT`. Luego comité de arranque mínimo (1 juez) valida hipótesis iniciales. Si `sin research útil`, sigue sin 1.R.

## Estructura hallable (2 reads) — canónica en proyecto

```
research/                           <- CANÓNICA (hermana de Project/ y .opencode/, creada por skill-init, versionada en git)
  _index.md                         <- READ 1: tabla machine-readable (compat: INDEX.md)
  LEARNINGS.md                      <- base de conocimiento acumulada (obligatoria con --autoresearch)
  _template/                        <- plantilla clonable
  YYYY-MM-DD-{slug}/                <- 1 experimento = 1 carpeta fechada (README.md + NOTEBOOK.md + metric.json + prompt.md + traces/)
.opencode/goals/<slug>/research/    <- MIRROR efímero (dual-write TTL 2 sprints, luego deprecado)
  INDEX.md                          <- READ 1 mirror
  2026-10-18-vec-bm25-hnsw/
    NOTE.md                         <- READ 2 mirror
    artifacts/ (opcional)
```

> **Regla nueva:** si `research/` no existe, Goal la crea vía `skill-init` (`_index.md` + `_template/` + `.opencode/skills/research/SKILL.md`). La canónica manda; el mirror solo facilita `read research/INDEX.md` legacy.

- **Carpeta:** `YYYY-MM-DD-{slug}/` — mismo naming que `skill-init` y `_index.md`. El delta (`m08`, `p03`) **no va en el nombre**: va en `metric.json.delta` y en el veredicto de `NOTE.md`. Sin `HHMM`, sin `auto/` (YAGNI). Si algún día coexiste `manual/`, se migra a `research/auto/` + `research/manual/` y se filtra por campo `type`.

  Ejemplos (carpeta canónica; el delta vive dentro):
  - `2026-10-18-gate-calificado/` (delta -8.1% en `metric.json`)
  - `2026-10-18-coalescing-batch/` (delta -4.9% adicional)
  - `2026-10-18-holdout-live/` (delta -2.1% degradación validada)
- **INDEX.md** (append-only, fuente de verdad para early-stop):
```md
# Research Index — <slug>
early_stop: 3
| fecha | slug | type | verdict | hallazgo | consecutive_fails | comites | link |
| 2026-10-18 | vec-bm25-hnsw | auto | fail | hnsw pierde recall en <10k | 1 | 0 | ./2026-10-18-vec-bm25-hnsw/NOTE.md |
```
- **NOTE.md** por experimento (con frontmatter `verdict: fail/success`) — 6 apartados, el cuaderno completo:
```
---
verdict: fail
metric_value: 0.21
delta: -0.02
oos_value: 0.19
oos_delta: -0.01
based_on: LEARNINGS.md#2026-10-17 (el índice no movía p95)
---
## Hipótesis
## Protocolo (prueba hecha)
## Resultado (métrica + proof)
## Hallazgo (positivo / negativo)
## Interpretación
## Siguiente prueba
```

## Loop 1.R — determinista y acotado (genérico por métrica)

- **Presupuesto:** max 5 ciclos, cada ciclo = 1 iter del límite global de 15 (no presupuesto paralelo) + `budget` dual `max_tokens + max_wall_time` por tarea. `INDEX.md: early_stop: 3` → si `consecutive_fails ==2` invoca comité (1 de 6), si `>=3` para definitivo.
- **Métrica genérica (no hardcode):** definida en FASE 0b como `research: {metric_key, target, direction, harness}` en `PLAN.md` y materializada en `research/YYYY-MM-DD-{slug}/metric.json` `{metric_key, baseline, result, delta, optimizer, dataset_hash, direction}` (0.0-1.0). `tokens_por_exito` es solo un `metric_key` más del `MetricRegistry`, no el default.
- **Harness hermético frozen:** `harness_hash = sha256(harness_code + metric_def + prompt.md + seed + docker.lock)` versionado en `research/.harness.lock`. Misma hipótesis + mismo hash → mismo resultado. Sin hash → REJECT.
- **Proof de ejecución (ruta única):** `research/<exp>/traces/<harness_hash>.r1.proof` y `.r2.proof` para la réplica x2. JSON `{run_id, harness_hash, dataset_hash, seed, started, ended, exit_code, metric_value}`. Se resuelve con `logger/index.js:validateProof`; prohibido duplicar el literal en SKILL.md/team y prohibido `lab/traces/` (TTL 72h).
- **Un ciclo:** hipótesis falsable → parche mínimo → `harness` genérico → `metric.json` `{metric_value, delta}` → escribe `NOTEBOOK.md` (o `NOTE.md` mirror) + actualiza `research/_index.md` (y mirror `INDEX.md`).
- **Promoción a steps/:** solo si `delta` supera `target` genérico, **replica 2 mediciones** con mismo `harness_hash`, **mejora también en el examen guardado** (§Examen guardado) y pasa `tests no mentirosos`. Si no, se revierte el árbol, pero **nunca sin antes guardar el cambio** (ver §Versiones del sujeto).

## Espacio de cambio declarado (antes de tocar)

Antes del primer ciclo se escribe **qué se puede tocar y qué no**. Sin esto, cualquier mejora es sospechosa.

- **`research/CHANGE_SPACE.md`** (creado en FASE 0b, junto al sujeto):
  ```
  ## Se puede tocar
  - scorer.py (funciones de puntuación)
  - params.json (umbrales)
  ## Prohibido tocar
  - harness/ (el medidor no se cambia a mitad)
  - datos de validación
  - tests/ (los tests no se ajustan para pasar)
  ```
- **Regla dura:** un parche fuera de `Se puede tocar` → ciclo inválido (REJECT), aunque mejore la métrica.
- **Cambio de alcance:** si hace falta tocar algo prohibido, se propone en `NOTE.md` y se actualiza `CHANGE_SPACE.md` **antes** del parche, dejando constancia del motivo.
- **Tablero:** se muestra como panel «Espacio de cambio».

## Examen guardado — fuera de muestra (obligatorio si hay muestra)

Repetir la medición dos veces solo prueba estabilidad; el examen guardado prueba que no fue chiripa.

- **Reparto:** al declarar el dataset, si hay **muestra suficiente** (≥50 casos) se reserva **~20%** que **no se usa nunca** para proponer ni ajustar. Si no hay muestra suficiente, se anota `oos: no_aplica` con el motivo y no se inventa.
- **`research/holdout/`**: copia del 20% + `holdout.json` `{n, total, pct, sha256, fecha}`. Se crea una sola vez.
- **`holdout_hash`** entra en `harness_hash`; cambiarlo invalida la comparación con las pruebas anteriores.
- **Cuándo se mide:** solo al validar una mejora real (antes de crear versión) y al cerrar el goal. Nunca en el bucle de hipótesis.
- **Promoción:** exige mejorar en entrenamiento **y** en el examen guardado. Si mejora en uno y empeora en el otro, es sobreajuste: no se promueve y se anota en `LEARNINGS.md`.
- **`metric.json`** añade `{oos_value, oos_delta}`. El veredicto (`success`) solo es válido si `oos_delta` también mejora o se mantiene.
- **Prohibido:** mirar el examen para elegir la siguiente hipótesis. Una mirada = el examen deja de valer y hay que repartir otro.

## La crítica como señal (no solo el número)

El número dice si mejoró; lo escrito al fallar dice **por dónde seguir**.

- **`LEARNINGS.md`** no es un diario: cada entrada lleva `qué falló` + `pista` (1 línea accionable).
- **`based_on:`** en el frontmatter de cada `NOTE.md` cita la línea concreta (de `LEARNINGS.md` o del `## Siguiente prueba` anterior) que originó la hipótesis. Sin `based_on` → ciclo inválido.
- **Regla:** si la pista contradice el resultado, se corrige la pista; no se ignora.
- **Cierre:** `ROADMAP.md ## Siguiente` debe salir de la última pista, no de una idea nueva sin relación.

## Versiones del sujeto (obligatorio, anti-pérdida)

Lo que se investiga es un archivo concreto (el «sujeto»). Se versiona **el archivo**, no solo el parche.

- **Declarar el sujeto:** FASE 0b anota en `PLAN.md` `research: {files: [...]}` (habitualmente 1 script). Si no está, el primer ciclo lo fija y lo escribe en `research/VERSIONS.md`.
- **v000 — original intacto:** antes de tocar nada, copia exacta a `research/versions/v000-original/` + `meta.json` con `{sha256, fecha, metric.json baseline}`. Nunca se modifica ni se borra.
- **Ciclo:** se edita el archivo en su sitio (no copias sueltas). Antes de revertir, `research/<exp>/artifacts/change.patch` (`git diff`); sin parche guardado está prohibido `git checkout --`, `reset --hard` o borrar.
- **Mejora real** (`delta` supera objetivo **y** réplica x2): snapshot `research/versions/vNNN-<exp>/` con copia de los `files`, `meta.json` `{métrica, delta, sha256, fecha, experimento, harness_hash}` y `NOTE.md` enlazado. `vNNN` = correlativo, nunca se reutiliza.
- **`research/VERSIONS.md`** (append-only): `versión | fecha | experimento | métrica | delta | archivos`. Es la tabla de versiones; `research/BEST.md` apunta a la mejor (versión, no parche).
- **Empate:** no se crea versión nueva. Solo estrictamente mejor.
- **Cierre:** si el árbol final no es la mejor versión, se restaura esa (copia de `versions/vNNN/`) antes de cerrar. Prohibido cerrar dejando el proyecto peor que la mejor versión.
- **Git opcional:** además, `git tag goal/<slug>/vNNN` si el proyecto es repo. El tag no sustituye la copia.
- **Tablero:** `VERSIONS.md` se muestra en la investigación con enlace al contenido de cada versión.

## Conocimiento acumulativo (obligatorio en ambos modos)

El aprendizaje no vive en el contexto del agente: vive en disco y se lee antes de cada hipótesis.

- **`research/LEARNINGS.md`** — una entrada por prueba (máx. 3 líneas): qué se aprendió y qué descartar. Se lee (READ 2) **antes** de proponer la siguiente hipótesis, no después.
- **`research/ROADMAP.md`** — la ruta, reescrita al cerrar cada ciclo y nunca borrada:
  ```
  ## Camino recorrido   (hipótesis probada → resultado en una línea, en orden)
  ## Vivo               (hipótesis abiertas, con por qué)
  ## Descartado         (hipótesis muerta + motivo)
  ## Siguiente          (la próxima concreta, y la de después)
  ```
- **Regla anti-bucle:** prohibido repetir una hipótesis de `Descartado` salvo que se explique qué supuesto cambió.
- **Cierre:** si un goal termina sin mejora, `ROADMAP.md` deja las hipótesis vivas y el siguiente paso exacto para retomar.

## Contabilidad de ciclos (anti-parada-prematura)

El número no es una sugerencia: se cuenta en disco y manda.

- **Qué es un ciclo:** hipótesis escrita + parche aplicado + harness ejecutado + `metric.json` + fila en `_index.md` + `LEARNINGS.md`/`ROADMAP.md` actualizados. Leer, pensar o tocar un archivo **no** es un ciclo.
- **Registro:** `research/cycles.jsonl`, una línea por ciclo cerrado `{n, fecha, experimento, metric, delta, harness_hash}`. Es la única fuente para contar; si no hay línea, el ciclo no existe.
- **Cuota mínima antes de parar:** `/goal-research` = 5 ciclos · `/goal-autoresearch` = **15 ciclos**. Presupuesto máximo 20.
- **Parada legítima (solo tres):** objetivo alcanzado con réplica x2 · 10 comités seguidos · cuota agotada.
- **Prohibido parar** por «creo que ya está», por tiempo, por tokens o por cansancio. Si el agente cree que debe parar antes, escribe `## PARADA PROPUESTA` con motivo en `NOTE.md` y **sigue igualmente**.
- **Cierre:** con `ciclos < cuota` y sin objetivo, el estado es `bloqueado`, nunca `fin`.
- **Tablero:** muestra `ciclos N/cuota` en la investigación.

## Memoria (canónica en proyecto, no en Goal)

- **Detallada (CANÓNICA):** `research/_index.md` + `research/YYYY-MM-DD-{slug}/NOTEBOOK.md` + `metric.json` (append-only, nunca se borra, versionada en git). Mirror ` .opencode/goals/<slug>/research/INDEX.md` se mantiene por TTL dual-write.
- **Resumida:** 1 línea agregada a `CONTEXT.md` FIFO (`research: mejor delta <hash> @ research/YYYY-MM-DD-{slug}/`) + 1 línea en `LOG.md` + 1 línea en `INDEX.md` global apuntando a `research/_index.md`.
- **Descubrimiento:** `read research/_index.md` (READ 1) → sabes si parar y qué experimento abrir → `read research/YYYY-MM-DD-{slug}/NOTEBOOK.md` (READ 2). Con `research.deep=true` el READ 2 es `research/LEARNINGS.md` (conocimiento acumulado) y el `NOTE.md` se abre solo para el experimento concreto. Compat: `read .opencode/goals/<slug>/research/INDEX.md` → mirror.

## Límites y comité

- Loop: si `consecutive_fails ==2` → invoca **FASE 1b comité (consume 1 de 6)** con `## RESEARCH` acumulado; tras veredicto vuelve a 1.R. Si `consecutive_fails >=3` (early_stop) → para definitivo.
- **Trigger mini-skill por comité:** si FASE 1b resuelve un bloqueo (2 fallos → comité → fix), propone candidata mini-skill anti-patrones en `research/YYYY-MM-DD-{slug}/NOTE.md` con lección; promoción solo si pasa tests no mentirosos + replica x2 + auditor PASS (ver `mini-skills/README.md`).
- Techo global sigue siendo 15 iter / 6 comités en modo normal. Research normal nunca lo expande; solo `§Modo profundo` (`--autoresearch`) amplía el presupuesto de este goal.

## Modo profundo (`--autoresearch`)

Solo si `research.deep=true` (flag `--autoresearch` o alias `/goal-autoresearch`). Sin flag no aplica: manda el loop normal (early_stop 3).

- **Presupuesto:** `max_ciclos: 20` y **cuota de 15 ciclos completos** antes de poder parar, techo de iteraciones del goal 30 (SKILL.md §Reglas de parada), **10 comités consecutivos**, nunca más de 60 globales.
- **Disparo:** cada `consecutive_fails == 2` abre comité (formato FASE 1b) y **reinicia `consecutive_fails=0`** tras el veredicto; por eso pueden encadenarse hasta 10. Los comités 1-9 usan `skill({name:"goal-comite-internal"})`.
- **Última oportunidad:** cuando `comites_consecutivos == 9`, el siguiente comité (el 10.º) se invoca con `skill({name:"goal-comite-pro-internal"})` — doble refutación — en vez del standard. Su veredicto es el último: si marca camino, se ejecuta y un fallo cierra; si no marca camino, cierra directo.
- **Reinicio:** una mejora **replicada x2** (`delta` supera target + tests no mentirosos + examen guardado no empeora) pone `comites_consecutivos=0` y `consecutive_fails=0`. Sin réplica no reinicia.
- **Parada:** `comites_consecutivos >= 10` → `bloqueado` definitivo: último `NOTE.md` con qué falta, hipótesis descartadas y propuesta; no se invocan más comités.
- **Cuaderno:** `NOTE.md` con los 6 apartados (Hipótesis, Protocolo, Resultado, Hallazgo, Interpretación, Siguiente prueba).
- **Base de conocimiento:** `research/LEARNINGS.md` (append-only en el proyecto, máx 3 líneas por experimento: qué se aprendió y qué descartar). READ 1 `_index.md` → READ 2 `LEARNINGS.md`; `NOTE.md` solo al abrir un experimento concreto.
- **Anti-simulación:** sin `harness_hash` + proof + `delta` real el ciclo no cuenta y no reinicia nada.

## Blindaje Karpathy — anti-simulación (obligatorio)

> Prioriza cautela sobre velocidad. Si el research simula, no cuenta. Este blindaje es verificable.

**Checklist pre-ciclo (si falta 1, el ciclo es inválido):**
1. **Think Before Coding:** `NOTE.md` trae `## Hipótesis` con supuestos explícitos + 1 alternativa simple descartada + 1 pregunta si hay ambigüedad. Sin esto → REJECT.
2. **Simplicity First:** parche toca solo lo pedido (≤50 líneas o justificado). Prohibido añadir flags/configs no pedidos. Si 200→50 posible, reescribe.
3. **Surgical:** solo archivos de `block.json` ledger. Orphan imports/variables que tu parche deje → bórralos. No toques formato adyacente.
4. **Goal-Driven + Real + Zapatito de cristal (genérico):** cada ciclo ejecuta **plan completo verificado** (FASE -1→1) sobre tarea ancla LARGE, mide **métrica genérica `metric_key` real** (no deltas simulados, no `tokens_por_exito` fijo), con `harness_hash = sha256(harness_code+metric_def+prompt.md+seed)` hermético frozen, `L0-L3` reales y `diagnosis/<id>/{trace.json,diff.patch}`. Simulación sin harness → REJECT. **Anti-zapatito:** la mejora debe consolidarse en 3-4 pruebas distintas con supuestos diferentes (ej: LARGE auth 6-archivos, SMALL 3-archivos, doc-batch 5 docs, ambiguo sin criterio) + **holdouts privados rotativos**. Comité elige las 3-4 tareas de validación en FASE 0b; promoción solo si mejora en ancla AND ≥2/3 holdouts con `metric_key` genérica. Una sola tarea → no promueve. `tokens_por_exito` solo válido si `metric_key == "tokens_per_success"` explícito.
5. **Iteración hasta 3 fails reales:** no es 1 prueba. El loop sigue hasta `consecutive_fails>=3` con ciclos completos y largos (horas si hace falta). Cada ciclo = 1 iter del techo 15. Comité obligatorio en `==2` antes de parar (el comité decide siguientes supuestos/holdouts).
6. **Promoción:** solo si `delta` mejora vs mejor basal en ancla + holdouts (≥2/3) Y replica x2 con mismo hash + tests no mentirosos PASS. Veredicto en `NOTE.md` + `INDEX.md` hallable en 2 reads.
