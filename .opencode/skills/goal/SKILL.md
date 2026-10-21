---
name: goal
description: "Encarga un objetivo, crea plan seccional con agente plan y lo ejecuta; comité solo al atrancarse. Úsalo cuando quieras ejecutar un objetivo con plan verificable."
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "false"
  opencode/autoinvoke: "true"
---

Objetivo: $ARGUMENTS

Si el objetivo viene vacío, pide 1 sola pregunta aclaratoria y no avances.

**Flags:** `--full` fuerza flujo completo (comité → plan → iteración) sin clasificar; `--research` activa auto-research para bajar métrica (ver FASE 1.R). Alias `/goal-full` inyecta `--full`, `/goal-research` inyecta `--research`. Precedencia: `CLI flag > opencode.json goal.mode > auto`. Sin flag, clasifica normal.

## FASE -1 — Grill me (solo si hace falta)

Tras razonar el objetivo en 30 segundos: si está suficientemente claro (qué hay que conseguir, dónde, cómo se verifica), empieza directo sin preguntar. Si falta contexto crítico, hay ambigüedad real o 2+ interpretaciones válidas, haz un **grill me** corto: max 5 preguntas concretas, cada una con tu recomendación por defecto. No interrogues por rutina. Ejemplos de cuándo SÍ: no se sabe el alcance, faltan archivos/entorno, hay 2 enfoques con coste distinto. Cuándo NO: el objetivo dice qué + dónde + done criteria.

## FASE 0 — Clasifica + check-first (siempre, sin comité)

> Bypass: si `$ARGUMENTS` contiene `--full` o `--mode=force` → salta clasificación, marca `mode=full`, va directo a FASE 0b con plan seccional completo y `pre_comite` según p_fail (sin vía rápida TRIVIAL). Si no, clasifica normal.

1. Genera un `slug` de 2-4 palabras (ej: `auth-email`). Todo vive bajo `.opencode/goals/<slug>/` (nunca en raíz, nunca sueltos):
   - `PLAN.md` — plan hipótesis + tabla de pasos
   - `steps/NN-<nombre>.md` — 1 brief autocontenido por paso
   - `LOG.md` — append de iteraciones (solo de este goal)
   - `CONTEXT.md` — memoria viva, max 50 líneas, formato fijo + FIFO
   - `INDEX.md` global en `.opencode/goals/INDEX.md` — tabla `slug | objetivo | estado | fecha | huella` para detectar colisiones y reuso
   - Regla de aislamiento: solo lees/escribes tu carpeta `<slug>/`. Prohibido leer `LOG.md`/`CONTEXT.md` de otros goals. El check-first solo compara `PLAN.md` + `INDEX.md`, nunca mezcla logs.
   - Migración: si existen `GOAL_*/` o `GOAL_*.md` sueltos en raíz (versión vieja), muévelos a `.opencode/goals/<slug>/` o a `.opencode/goals/archive/<slug>-<fecha>/` al primer uso.
2. Clasifica según `ENJAMBRE-RULES.md` (calibrado enjambre v1.1, overhead 62k/sesión): **TRIVIAL** (≤500 tok o 1 archivo simple, <30s razonamiento) / **SMALL** (≤10k tok trabajo real, 3-5 archivos simples) / **LARGE** (>10k tok, multi-archivo complejo). El comité vive en FASE 1b y, condicional, en FASE 0b si `pre_comite=true` (p>0.55, conf>0.55; zona gris 0.43-0.55 → `deferred`); nunca en FASE 0 directo.
   - **TRIVIAL → vía rápida, sin plan:** no crea `PLAN.md` ni `steps/`. Va directo a ejecutar + verificar + tests en FASE 1-fast (ver abajo). Solo deja `.opencode/goals/<slug>/LOG.md` de 3-10 líneas y registra 1 fila en `INDEX.md`. Por qué: cada subagente paga ~62k overhead; en trivial supera 136:1 al trabajo real.
   - SMALL/LARGE → sigue al paso 3.
2b. Gate find-skills condicional (antes del plan, solo si SMALL/LARGE): si clasificación >=SMALL → ejecuta `goal-discovery --query="$ARGUMENTS" --json --cache-ttl=24h --out=.tmp/find-skills-<hash>.json` stateless con registry_hash + single-flight cache ~/.cache/opencode/find-skills/ (TTL 24h, invalidación por registry_hash), output efímero no muta block.json/STATE, planner lee .tmp/*.json si existe. Si TRIVIAL → skip 0 tok log `skip: trivial`. Si offline o 0 hits → degrada graceful (no bloquea). Coste 800-1500 tok solo en SMALL+.
3. Check-first: `glob .opencode/goals/*/PLAN.md` + lee `.opencode/goals/INDEX.md`. Si hay match de slug u objetivo similar:
   - Lee el PLAN + valida premisas contra código y `commands/*.md` actuales.
   - Vigencia por **hash, no por fecha**: guarda en `PLAN.md` `## Huella: <git HEAD corto> + <hash de archivos tocados>`. Es válido solo si HEAD y hashes siguen iguales y las premisas (archivos existen, API no cambió, objetivo no divergió) siguen ciertas. La edad (7d orientativo) no invalida por sí sola. Si está podrido → archívalo a `.opencode/goals/archive/<slug>-<fecha>/` y sigue como si no existiera. Anota en el output `caché: hit/miss` para medir hit-rate.
   - Si es válido → propone `reusar / extender` y salta a FASE 1. No regeneres ni convoques comité. Actualiza `INDEX.md` (`estado`, `fecha`, `huella`).
4. Si no hay plan válido → pasa a FASE 0b (plan con agente `plan`, condicional). Si es SMALL sin plan → mini-plan directo de 3-5 pasos en `PLAN.md` (sin `steps/` si son ≤3 pasos). Si el plan reusado es válido → salta a FASE 1. TRIVIAL ya salió por vía rápida, no llega aquí.
5. Lección de contexto: lee `memory/lessons.md` (corto, tope 50 líneas). Si el patrón del objetivo coincide con una línea `→ skill: <nombre>`, carga esa micro-skill por nombre exacto antes de planear y anota `skill-uso: <nombre> | fecha` en lessons.md. Si coincide con `→ skill-archivada: <nombre>`, propón re-promoción en FASE 2. No existe índice aparte: lessons.md ES el índice (anti split-brain).
6. Señal pre-comité (A_conditional v2 — planner-opt 2026-10-21 blindado): estima `p_fail` + `confidence`. Usa `noul(tarea, "alta incertidumbre: multi-stack, ambiguedad, migracion, seguridad o trade-off")` o keywords. Si `p_fail > 0.55` y `confidence > 0.55` y sin veto explícito y no es TRIVIAL → `pre_comite=true` (consume 1/60); si `0.43 < p_fail ≤ 0.55 && conf>0.55 && ambiguo` → `pre_comite=deferred` (no consume, log `zona-gris p=0.xx conf=0.yy deferred` y delega a FASE 1b si falla, ajusta `-0.02` en `memory/lessons.md`); resto `false`. En ambiguo sin criterio, grill-me estricto. Respeta "sin comité" aunque p alto. Anota `pre_comite: true/false/deferred (p=0.xx, conf=0.xx)`.

## FASE 0b — Plan con agente `plan` (A_conditional)

Solo entra aquí si FASE 0 no encontró plan válido.

Usa el agente **`plan` nativo de opencode** (primary `plan`: analiza sin modificar código, `edit: deny` / `bash: deny`) para diseñar la partición — no un agente `build` normal. Por qué: `plan` no contamina el repo mientras explora y propone. Flujo: `plan` diseña → **si FASE 0 marcó `pre_comite=true` (p>0.55, conf>0.55, sin veto) → comité pre-plan de 5 agentes sobre la partición (mismo formato FASE 1b, consume 1/60, sin research) y ajusta PLAN.md; si `deferred` (zona gris 0.43-0.55) → log `zona-gris p=0.xx deferred` sin comité y delega a FASE 1b si falla; si `false` → plan directo sin comité** → orquestador materializa `.md`. Comité solo en alta incertidumbre; resto en FASE 1b.

**Auto-research (opcional, ver `research/controller.md`):** si el objetivo trae `--research` / `research: {metric, target, harness}` O el agente detecta en FASE -1 métrica cuantificable + harness determinista, propone en `grill me` activar `research.enabled=true` (nunca TRIVIAL); si `--research` sin `metric+harness` cuantificable → REJECT `research requiere metric cuantificable + harness determinista; usa --full sin research o define metric` (no crea `research/INDEX.md`). Si se activa, `plan` define `research: {metric, target, harness, harness_hash}` en `PLAN.md` y orquestador inicializa `research/INDEX.md` con `early_stop: 2` (hallable 2 reads).

1. Carga `skill({name:"goal-plan"})` y delega: el agente `plan` propone partición (ver esa skill: Regla 0/1 + robust-first). Si FASE 0 marcó `pre_comite=true` (p>0.55, conf>0.55) → invoca `skill({name:"goal-committee"})` pre-plan (consume 1/60) y ajusta PLAN.md; si `deferred` zona gris 0.43-0.55 → sin comité, log `zona-gris deferred` y ajusta `-0.02`; si `false` sin comité. Escribe en `LOG.md` `## PLAN — <objetivo>` + `pre_comite: true/false/deferred (p=0.xx, conf=0.yy)`.
2. Materializa en archivos editables (el humano puede editar antes de ejecutar):
   - `PLAN.md` con: `## Objetivo`, `## Éxito verificable` (3-7 criterios machine-chequeables), `## Pasos` (tabla `N | nombre | archivos | depende-de | paralelizable?: hipótesis eficiente SÍ/NO + por qué | verificar`), `## Riesgos`, `## Estado`, y si algún paso es `SÍ`, bosqueja `.opencode/goals/<slug>/block.json` inicial con `claims` por paso (ledger informativo, no lock, ver `block.schema.json`; lo escribe orquestador, workers solo leen).
   - `steps/NN-<nombre>.md` por paso: objetivo del paso, archivos que toca, depende-de, `paralelizable?:` como **hipótesis eficiente no vinculante** + `por qué no compensa` si es NO, criterio done (comando exacto), **tests exigidos** (ver regla de tests abajo).
   - La columna `paralelizable?` es predicción falible y de eficiencia. El runtime la verifica con `block.json` + Regla 1/2, nunca la obedece a ciegas; si hay solape o <10k tok, degrada a secuencial y lo anota.

## FASE 1.R — Auto-research opcional (determinista y acotado)

Controlador externo: `research/controller.md` (no infla SKILL.md). Si `research.enabled=false`, esta fase no existe y coste 0. Si `true`: deep research inicial (3-7 bullets con fuente en `LOG.md ## RESEARCH-INIT`) → comité de arranque mínimo → loop 1.R max 5 ciclos en `.opencode/goals/<slug>/research/YYYY-MM-DD_<slug>/NOTE.md` con `research/INDEX.md` hallable en 2 reads (`INDEX.md` → `NOTE.md`). Cada ciclo = 1 iter del límite global de 15; early-stop si 2 fallos consecutivos (`consecutive_fails >=2`) → invoca FASE 1b (consume 1 de 60). Promoción a `steps/` solo con `delta` replicado x2 + tests no mentirosos. Detalle completo en `research/controller.md`.

## FASE 1 — Runtime soberano (el plan propone, el runtime dispone)

Todas las rutas (`PLAN.md`, `LOG.md`, `CONTEXT.md`, `steps/`) viven dentro de `.opencode/goals/<slug>/`. Si existe `research/`, también es parte de `<slug>/` y se rige por `research/controller.md`. Nunca toques la carpeta de otro goal.

Repite hasta que TODOS los criterios de éxito pasen:

1. Toma el siguiente paso `pendiente` de `PLAN.md`. Lee su `steps/NN-*.md`.
2. **Verificación de disjunción + block.json (obligatoria, regla 1 enjambre):** antes de paralelizar comprueba 4 condiciones TODAS: (a) interfaces estables, (b) archivos disjuntos (`block.json` — `block.schema.json`), (c) I/O-bound independientes (no CPU modelo), (d) sin `dependsOn` cruzado entre subtareas (ej: `migrations→api`). `claims[].dependsOn?: string[]` opcional; orquestador valida DAG (sin ciclos); si ciclo/solape/dependencia → **degrada a secuencial directo en 1 agente (sin pagar ~62k por subagente extra)** + log `degrada: dependencia transversal <A>→<B>`. Por defecto secuencial.
3. **Regla de despacho (enjambre como skill, no agente — regla 2 enjambre):**
   - 1 paso → directo (sin subagente).
   - 3+ docs/informes disjuntos → **writer-batch en 1 sesión** (1 sesión N archivos, -77% tokens vs N workers: 71k vs 327k en 5 docs).
   - ≥2 pasos disjuntos + trabajo >10k tok → subagentes en paralelo con mensaje mínimo `lee X, escribe Y` (sin contexto redundante). Si no, secuencial.
   - Nunca pagues ~62k de overhead por trabajo <10k tok. SMALL complejo (≤5k tok real) va directo sin subagentes.
4. Ejecuta (ediciones mínimas), verifica inmediatamente con el comando de `verificar` del step. No declares éxito por inspección. Aplica la **regla de tests** de abajo: sin tests el paso no se marca hecho.
5. **Auto-compact check (Muse Spark 1.2):** tras marcar el bloque, si `tokens_ventana >=68%` → ejecuta auto-compact del punto 3 de FASE 1-auto (checkpoint + extractivo + reinyecta objective.lock.json). Si no hay trigger, sigue sin compactar. Anota en LOG `compact: skip/summarize (ventana X/128k, drift Y)`.

6. Actualiza **en el mismo paso**: `PLAN.md` (estado ✅/❌), `LOG.md` (append `## Iteración N — Intentado/Resultado/Error exacto/Aprendizaje`), `CONTEXT.md` con plantilla fija (sobrescribe, FIFO: lo más viejo se expulsa primero, nunca narrativa libre):
   ```
   ## Funciona (max 10 líneas)
   ## Falla (max 10 líneas)
   ## Decisiones (max 10 líneas)
   ## Pendiente (max 10 líneas + comité gastado X/60)
   ## Caché (1 línea: hit/miss + huella)
   ```
7. Si fallo → reintenta 1 vez con enfoque distinto (max 2 intentos por punto). Si tras 2 intentos sigue sin conseguirse → **re-trazo ligero obligatorio (sin comité)**: 1 intento de replanificación acotada (dividir el paso, recortar alcance o cambiar el orden en `PLAN.md` + 1 línea en log) **+ re-estima `p_fail` y `fan-out`**. Gate escalado: si tras re-trazo se cumple 1 de 4 (fan-out>3 archivos, `p_fail>0.55`, ≥2 dominios/research externo, estimación x2) → **escala SMALL→LARGE** y pasa a FASE 1b con `pre_comité`+`block.json`+enjambre; si 4 negativos (fallo por typo/flaky) → mantiene SMALL revisado. Solo si re-trazo+gate también falla → `bloqueado`.

### FASE 1-fast — Vía rápida TRIVIAL (sin PLAN, sin comité)

Solo para TRIVIAL: ejecuta fix directo, verifica con comando/test, deja `LOG.md` 3-10 líneas (intentado/resultado/error) **y lección obligatoria en `memory/lessons.md`** (tag `coste: alto|medio|bajo` — sin lección = **fuga**). Sin `PLAN.md`, sin `steps/`, sin comité, sin research. Guard: instrumenta `intentos_trivial` en STATE; si 2 fails → `escala TRIVIAL→SMALL` crea `PLAN.md` mini 3 pasos + LOG `escala trivial→small (2 fails)`; 3er fail → FASE 1b.

### Regla de tests (obligatoria) — robustos, anti-trampas y diagnósticos

**Disparo dual:** se activan **auto** en cada bloque FASE 1 (verify) y **a demanda** con `/goal_test` (default strict). `/goal_test --off --reason="..."` exige motivo y deja traza. Ambos usan mismo `core/checks` — no hay dos lógicas.

- **L0 Inversión (falsable, bloqueante):** todo test debe **fallar sin el fix y pasar con el fix**. El harness revierte 1 vez el patch y ejecuta. Si pasa en verde → REJECT anti-trampa.
- **L1 Contrato + anti-trampas (bloqueante <2s):** linter AST que bloquea: `assert True`/`expect(1).toBe(1)`, `expect(x).toBeTruthy()` sin valor, mocks que sustituyen la lógica del paso sin `verify`, `skip/todo/xit`, snapshots vacíos, y E2E sin assert sobre estado. `coverage` solo no aprueba.
- **L2 Propiedad/invariante (bloqueante <30s):** 1 propiedad con fast-check ≥100 casos (idempotencia, round-trip, orden) o 1 happy +1 borde +1 error por unidad. En web/UI: Playwright 1 happy +1 error visible con screenshot; si no aporta, 1 línea de por qué.
- **L3 Mutación dirigida (condicional):** Stryker solo sobre archivos tocados por el goal, threshold 70% inicial (sube a 80% solo si FP<10% en 20 goals). Bloqueante si `complexity=high` o `risk=core`, informativo si `low`. Métrica `mutation_score` reportada siempre.
- **Flaky gate:** 3 reruns con seed distinto; si `flaky_rate >5%` → quarantine, no cuenta como verde.
- **Diagnóstico obligatorio:** todo fail escribe `/.opencode/goals/<slug>/diagnosis/<id>/{trace.json,diff.patch,snapshot}`. Sin artefacto el run es inválido. `LOG.md` debe citar `diagnosis/<id>` con causa.
- **Frontera borrable vs permanente:** probes en `lab/`, `research/probes/`, `tests/_probe_*/` (TTL 72h, excluidos CI). Invariante: `rm -rf lab/ research/probes/ tests/_probe_*/ ; npm test` sigue verde (`clean-lab.py` + `goal.isolation.test.ts`). Borrable deja línea en `LEDGER.md`.
- **Done del step:** comando exacto + resultado + `hash` + `falsable:true` + `mutation_score` si L3 aplica.

## FASE 1b — Desbloqueo (solo si 2 veces no sale, max 2 por punto; puede modificar el plan)

Dispara SOLO cuando la implementación no se consigue 2 veces en el mismo punto. Si no, no hay comité.

`skill({name:"goal-committee"})` — ver esa skill para flujo completo (deep research + assumptions + 5 agentes + refutación + juez). Esta FASE solo orquesta: congela `## BLOQUEO`, invoca la skill, aplica su veredicto (puede reescribir PLAN.md/steps y recalcular `paralelizable?`), anota `## COMITÉ — veredicto N/2: ...` y vuelve a FASE 1. Límite por punto: max 2; tras 2º → `bloqueado-definitivo`. Techo global 60. Zona gris (confidence 0.55-0.70 en p_fail): no fuerces comité, deja que FASE 1b lo rescate si falla y loguea `pre_comite:false->true` para auto-ajustar umbral.

## FASE 1-auto — Autonomia iterativa (opcional, sin humano)

Activala con `--autonomy` o si el objetivo es LARGE y estimas >15 iters. Todo el progreso vive en disco, nunca solo en el chat.

1. **STATE validado:** al iniciar crea `.opencode/goals/<slug>/STATE.json` validado contra `STATE.schema.json` (requeridos: slug, status, iter, comites_totales, comites_por_punto, beat_ts, watchdog_timeout_min=20, hash_fase0). Antes de cada escritura destructiva guarda `STATE.snapshot.json`; si la validacion falla al leer, restaura snapshot. Cada inicio de bloque → `beat` (actualiza beat_ts); al pasar tests → `advance`; al fallar 2x en mismo punto → `pause` si toca.
2. **Itera hasta exito o pause:** repite FASE 1 normal pero con STATE. Si un punto exige 3er comite (ya van 2) → **no lo invoca**: hace `pause` trazable con veredicto+reversion+siguiente paso y deja STATE en `paused` para retomar con `opencode goal --resume <slug>` o watchdog. Watchdog 20min (si existe tarea programada) solo despierta si `status==running` y `now-beat_ts > timeout`.
3. **Auto-compact Muse Spark 1.2 (entre bloques, extractivo, con pin):** al crear el goal guarda `.opencode/goals/<slug>/objective.lock.json` (objetivo literal + constraints + hash PLAN.md) — inmutable y reinyectado siempre como prefijo, nunca compactado. Entre bloques (nunca intra-bloque) si `ventana >=68% (87040/128k)` o bloque verificado con `verify` verde, el orquestador: (a) checkpoint `.opencode/goals/<slug>/checkpoints/block-N.json`, (b) compacta solo charla/trazas con prompt extractivo verbatim 30% (mantiene decisiones, bloqueos y needles literales, dropea charla), validado contra schema `Objetivo|Estado|Decisiones|Bloqueos|Próximos`. Si validación falla o drift `cosine(objective.lock, remembered) <0.60` → aborta compact y restaura checkpoint. Política por bloque `keep/summarize/skip` según `keep` si decisiones abiertas. Modelo siempre Muse Spark 1.2 `temp 0` para compact; FASE 1-fast nunca compacta.
4. **Destructivo con gate:** toda accion irreversible pasa por `gate_action(kind="destructive")` → snapshot previo obligatorio + log; sin snapshot no se ejecuta.

## FASE 2 — Auto-improve (cierre de objetivo, siempre)

Constitución completa en `mini-skills/README.md` (única fuente de reglas; este resumen no la duplica). En el cierre, en orden:

1. Mina `LOG.md` + `CONTEXT.md` → extraer **max 3 lecciones nuevas** a `memory/lessons.md` (batch obligatorio si excede el tope de 50).
2. Evaluar candidaturas (repetición ≥2 en lessons.md, o fallo+comité+fix) → promover al registro `.opencode/skills/` SOLO si cumple umbral adaptativo por coste (alto=1 / medio=3 / bajo=5 menciones) y promoción blindada (README §3). Skill con `opencode/autoinvoke: "false"`; nombre limpio; colisión → sufijo. Prohibido crear índice aparte o escanear directorios.
3. Ciclo de vida: skill sin uso 30 días → archivar (mover a `memory/skills-archive/`, **nunca borrar**; <30 días de vida es intocable). Patrón que matchea una skill archivada → propone re-promoción.
4. Parches al SKILL.md de goal: solo modo **propose** en `memory/proposals.md` con backup versionado; max 1 por goal.
5. Cierra con línea de métricas (README §7) en `LOG.md`: `métricas: goals | promovidas | hit-rate | archivadas | fuga-lessons`.

## Memoria — límite duro estilo Hermes

Fuente: `memory/current.md` (canónica, `memory.md` es espejo). Además, `memory/lessons.md` guarda aprendizajes con tag `coste` (tope 50 líneas, batch obligatorio, formato en `mini-skills/README.md` §1): se lee en FASE 0 y se escribe en FASE 1-fast y FASE 2. Límite 2.200 chars. No hay FIFO silencioso: si un `add`/`patch` excede, devuelve error con `current_entries` y exige **un batch** que libere (remove/patch) + añada en la misma operación. Si >80% consolida antes de añadir. Ver `memory/README.md` para protocolo `YYYY-MM-DD_tema` y 2 reads `memory/INDEX.md` → `memory/current.md`.

## Reglas de parada

- Termina SOLO con evidencia de cada criterio de éxito (incluyendo tests + E2E web si aplicó).
- Para a las 15 iteraciones o 60 comités totales sin completar: marca `bloqueado`, reporta qué falta, qué intentaste, veredictos en 1 línea, y propuesta.
- No pidas confirmación para iterar. Solo al terminar o bloquearte del todo.
- Nunca borres `.opencode/goals/<slug>/`. Es el entregable. Lo obsoleto va a `.opencode/goals/archive/`.

## Output final (formato cerrado, obligatorio)

Devuelve EXACTAMENTE estas 4 secciones, en este orden, sin añadir otras. Tono operativo, sin adornos.

### 1. Tecnicismo (max 1)
Una sola línea con el detalle técnico clave de la respuesta (decisión, causa raíz o contrato). Prohibido soltar 2+ tecnicismos aquí. Si hay más, van al resumen o al log, no aquí.

### 2. Resumen operativo (max 6 filas)
Tabla de lo hecho, probado y conseguido. Máximo 6 filas, 1 tecnicismo por fila como mucho:
`| Hecho | Probado con | Conseguido |`
Cada fila: qué se hizo → con qué se probó (comando/test exacto) → qué se consiguió (✅/❌). Sin tests reales, la fila es ❌.

### 3. Pendientes / ineficiencias (solo si hay)
Si no hay, escribe `Ninguno` y sigue. Si hay: lista corta de errores pendientes o ineficiencias detectadas (tests flaky, pasos degradados a secuencial, deuda, comité gastado). 1 línea por item, con causa en 5 palabras max.

### 4. Conclusión (3 líneas exactas)
Exactamente 3 líneas: línea 1 = estado (conseguido/bloqueado/parcial + por qué en 10 palabras), línea 2 = evidencia más fuerte (comando + resultado), línea 3 = siguiente paso concreto o `fin`.
