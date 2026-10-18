---
name: goal
description: "Encarga un objetivo, crea plan seccional con agente plan y lo ejecuta; comité solo al atrancarse. Úsalo cuando quieras ejecutar un objetivo con plan verificable."
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "true"
---

Objetivo: $ARGUMENTS

Si el objetivo viene vacío, pide 1 sola pregunta aclaratoria y no avances.

## FASE -1 — Grill me (solo si hace falta)

Tras razonar el objetivo en 30 segundos: si está suficientemente claro (qué hay que conseguir, dónde, cómo se verifica), empieza directo sin preguntar. Si falta contexto crítico, hay ambigüedad real o 2+ interpretaciones válidas, haz un **grill me** corto: max 5 preguntas concretas, cada una con tu recomendación por defecto. No interrogues por rutina. Ejemplos de cuándo SÍ: no se sabe el alcance, faltan archivos/entorno, hay 2 enfoques con coste distinto. Cuándo NO: el objetivo dice qué + dónde + done criteria.

## FASE 0 — Clasifica + check-first (siempre, sin comité)

1. Genera un `slug` de 2-4 palabras (ej: `auth-email`). Todo vive bajo `.opencode/goals/<slug>/` (nunca en raíz, nunca sueltos):
   - `PLAN.md` — plan hipótesis + tabla de pasos
   - `steps/NN-<nombre>.md` — 1 brief autocontenido por paso
   - `LOG.md` — append de iteraciones (solo de este goal)
   - `CONTEXT.md` — memoria viva, max 50 líneas, formato fijo + FIFO
   - `INDEX.md` global en `.opencode/goals/INDEX.md` — tabla `slug | objetivo | estado | fecha | huella` para detectar colisiones y reuso
   - Regla de aislamiento: solo lees/escribes tu carpeta `<slug>/`. Prohibido leer `LOG.md`/`CONTEXT.md` de otros goals. El check-first solo compara `PLAN.md` + `INDEX.md`, nunca mezcla logs.
   - Migración: si existen `GOAL_*/` o `GOAL_*.md` sueltos en raíz (versión vieja), muévelos a `.opencode/goals/<slug>/` o a `.opencode/goals/archive/<slug>-<fecha>/` al primer uso.
2. Clasifica según `ENJAMBRE-RULES.md` (calibrado enjambre v1.1, overhead 62k/sesión): **TRIVIAL** (≤500 tok o 1 archivo simple, <30s razonamiento) / **SMALL** (≤10k tok trabajo real, 3-5 archivos simples) / **LARGE** (>10k tok, multi-archivo complejo). El comité vive solo en FASE 1b, nunca en FASE 0.
   - **TRIVIAL → vía rápida, sin plan:** no crea `PLAN.md` ni `steps/`. Va directo a ejecutar + verificar + tests en FASE 1-fast (ver abajo). Solo deja `.opencode/goals/<slug>/LOG.md` de 3-10 líneas y registra 1 fila en `INDEX.md`. Por qué: cada subagente paga ~62k overhead; en trivial supera 136:1 al trabajo real.
   - SMALL/LARGE → sigue al paso 3.
3. Check-first: `glob .opencode/goals/*/PLAN.md` + lee `.opencode/goals/INDEX.md`. Si hay match de slug u objetivo similar:
   - Lee el PLAN + valida premisas contra código y `commands/*.md` actuales.
   - Vigencia por **hash, no por fecha**: guarda en `PLAN.md` `## Huella: <git HEAD corto> + <hash de archivos tocados>`. Es válido solo si HEAD y hashes siguen iguales y las premisas (archivos existen, API no cambió, objetivo no divergió) siguen ciertas. La edad (7d orientativo) no invalida por sí sola. Si está podrido → archívalo a `.opencode/goals/archive/<slug>-<fecha>/` y sigue como si no existiera. Anota en el output `caché: hit/miss` para medir hit-rate.
   - Si es válido → propone `reusar / extender` y salta a FASE 1. No regeneres ni convoques comité. Actualiza `INDEX.md` (`estado`, `fecha`, `huella`).
4. Si no hay plan válido → pasa a FASE 0b (plan con agente `plan`, sin comité). Si es SMALL sin plan → mini-plan directo de 3-5 pasos en `PLAN.md` (sin `steps/` si son ≤3 pasos). Si el plan reusado es válido → salta a FASE 1. TRIVIAL ya salió por vía rápida, no llega aquí.

## FASE 0b — Plan con agente `plan` (sin comité)

Solo entra aquí si FASE 0 no encontró plan válido.

Usa el agente **`plan` nativo de opencode** (primary `plan`: analiza sin modificar código, `edit: deny` / `bash: deny`) para diseñar la partición — no un agente `build` normal. Por qué: `plan` no contamina el repo mientras explora y propone. El enjambre no tiene agente propio de planes (solo orquestador + writer-batch + reviewers), así que `plan` es el correcto. Flujo: `plan` diseña → el orquestador materializa los `.md` (única escritura permitida en esta fase). **Prohibido convocar comité en esta fase.** El plan se hace directo, el comité queda reservado para desbloqueo (FASE 1b).

**Auto-research (opcional, ver `research/controller.md`):** si el objetivo trae `--research` / `research: {metric, target, harness}` O el agente detecta en FASE -1 que hay métrica cuantificable + harness determinista posible, propone en `grill me` activar `research.enabled=true` (nunca en TRIVIAL). Si se activa, `plan` define también `research: {metric, target, harness, harness_hash}` en `PLAN.md` y el orquestador inicializa `.opencode/goals/<slug>/research/INDEX.md` con `early_stop: 2` (esqueleto hallable en 2 reads).

1. Invoca a `plan` para que lea código (read/grep/glob) y proponga la partición en 3-7 pasos ejecutables con dependencias, SIN escribir código. Escribe en `LOG.md` `## PLAN — <objetivo>` con la propuesta recibida.
2. Materializa en archivos editables (el humano puede editar antes de ejecutar):
   - `PLAN.md` con: `## Objetivo`, `## Éxito verificable` (3-7 criterios machine-chequeables), `## Pasos` (tabla `N | nombre | archivos | depende-de | paralelizable?: hipótesis SÍ/NO | verificar`), `## Riesgos`, `## Estado`.
   - `steps/NN-<nombre>.md` por paso: objetivo del paso, archivos que toca, depende-de, `paralelizable?:` como **hipótesis no vinculante**, criterio done (comando exacto), **tests exigidos** (ver regla de tests abajo).
   - La columna `paralelizable?` es predicción falible. El runtime la verifica, nunca la obedece a ciegas.

## FASE 1.R — Auto-research opcional (determinista y acotado)

Controlador externo: `research/controller.md` (no infla SKILL.md). Si `research.enabled=false`, esta fase no existe y coste 0. Si `true`: deep research inicial (3-7 bullets con fuente en `LOG.md ## RESEARCH-INIT`) → comité de arranque mínimo → loop 1.R max 5 ciclos en `.opencode/goals/<slug>/research/YYYY-MM-DD_<slug>/NOTE.md` con `research/INDEX.md` hallable en 2 reads (`INDEX.md` → `NOTE.md`). Cada ciclo = 1 iter del límite global de 15; early-stop si 2 fallos consecutivos (`consecutive_fails >=2`) → invoca FASE 1b (consume 1 de 6). Promoción a `steps/` solo con `delta` replicado x2 + tests no mentirosos. Detalle completo en `research/controller.md`.

## FASE 1 — Runtime soberano (el plan propone, el runtime dispone)

Todas las rutas (`PLAN.md`, `LOG.md`, `CONTEXT.md`, `steps/`) viven dentro de `.opencode/goals/<slug>/`. Si existe `research/`, también es parte de `<slug>/` y se rige por `research/controller.md`. Nunca toques la carpeta de otro goal.

Repite hasta que TODOS los criterios de éxito pasen:

1. Toma el siguiente paso `pendiente` de `PLAN.md`. Lee su `steps/NN-*.md`.
2. **Verificación de disjunción + block.json (obligatoria, regla 1 enjambre):** antes de paralelizar comprueba 3 condiciones TODAS: (a) interfaces estables entre subtareas, (b) conjuntos de archivos disjuntos (verifica con `block.json` ledger — ver `block.schema.json`), (c) I/O-bound independientes (explorar/leer/redactar, no CPU del modelo). Si hay solape o dependencia → **degrada a secuencial**, anótalo en 1 línea en el log. Por defecto todo es secuencial hasta probar lo contrario.
3. **Regla de despacho (enjambre como skill, no agente — regla 2 enjambre):**
   - 1 paso → directo (sin subagente).
   - 3+ docs/informes disjuntos → **writer-batch en 1 sesión** (1 sesión N archivos, -77% tokens vs N workers: 71k vs 327k en 5 docs).
   - ≥2 pasos disjuntos + trabajo >10k tok → subagentes en paralelo con mensaje mínimo `lee X, escribe Y` (sin contexto redundante). Si no, secuencial.
   - Nunca pagues ~62k de overhead por trabajo <10k tok. SMALL complejo (≤5k tok real) va directo sin subagentes.
4. Ejecuta (ediciones mínimas), verifica inmediatamente con el comando de `verificar` del step. No declares éxito por inspección. Aplica la **regla de tests** de abajo: sin tests el paso no se marca hecho.
5. Actualiza **en el mismo paso**: `PLAN.md` (estado ✅/❌), `LOG.md` (append `## Iteración N — Intentado/Resultado/Error exacto/Aprendizaje`), `CONTEXT.md` con plantilla fija (sobrescribe, FIFO: lo más viejo se expulsa primero, nunca narrativa libre):
   ```
   ## Funciona (max 10 líneas)
   ## Falla (max 10 líneas)
   ## Decisiones (max 10 líneas)
   ## Pendiente (max 10 líneas + comité gastado X/6)
   ## Caché (1 línea: hit/miss + huella)
   ```
6. Si fallo → reintenta 1 vez con enfoque distinto (max 2 intentos por punto). Si tras 2 intentos sigue sin conseguirse → **re-trazo ligero obligatorio (sin comité)**: 1 intento de replanificación acotada (dividir el paso, recortar alcance o cambiar el orden en `PLAN.md` + 1 línea en log). Solo si ese re-trazo también falla → marca `bloqueado` y pasa a FASE 1b (ahí sí hay comité, y puede modificar el plan).

### FASE 1-fast — Vía rápida TRIVIAL (sin PLAN, sin comité)

Solo para TRIVIAL: ejecuta el fix directo, verifica con comando/test, deja `LOG.md` de 3-10 líneas (intentado/resultado/error). Sin `PLAN.md`, sin `steps/`, sin comité, sin research. Si en 2 intentos no sale, escala a SMALL (crea mini-plan) en vez de insistir.

### Regla de tests (obligatoria) + anti-trampas

- Todo paso con lógica nueva o cambio de comportamiento exige **tests unitarios** (crear o actualizar). Sin test que cubra el cambio, el paso NO se marca `hecho`.
- Criterio done del step debe incluir el comando exacto (ej: `pytest -q`, `npm test`, `go test ./...`) y su resultado.
- Si es **web/UI** (frontend, flujo en navegador, regresión visual o interacción): evalúa si una prueba con **Playwright** (`browser` / `playwright` MCP, skill `browser-qa` o `e2e-testing`) da una prueba más robusta que el test unitario solo. Si sí → crea la prueba E2E mínima (1 happy path + 1 caso de error/edge) y adjunta evidencia (comando + resultado, screenshot/video si aplica). Si no aporta robustez (ej: lógica pura), justifícalo en 1 línea en el log y quédate con unitarios.
- Los tests viven con el código del paso, no en `.opencode/goals/<slug>/`.
- **Prohibido tests tramposos.** Son nulos y el paso vuelve a `pendiente` si: asserts tautológicos (`assert True`, `expect(1).toBe(1)`), mocks que sustituyen la lógica que se dice probar, `skip`/`todo`/`xit` para esconder fallos, asserts sobre texto del error en vez de comportamiento, o tests que pasan igual con el fix revertido. Todo test debe: fallar sin el fix y pasar con el fix (verifícalo revirtiendo 1 vez cuando sea barato), asertar comportamiento observable (estado, output, efecto), y usar datos de borde reales (vacío, nulo, límite, error de red).
- Robustez mínima: 1 caso feliz + 1 borde + 1 error por unidad cambiada; en E2E web: 1 happy path + 1 error visible al usuario. Si el test es flaky (pasa/falla sin cambios), no cuenta como evidencia: estabilízalo o márcalo `bloqueado`.

## FASE 1b — Desbloqueo (solo si 2 veces no sale, max 2 por punto; puede modificar el plan)

Dispara SOLO cuando la implementación no se consigue 2 veces en el mismo punto: 2 fallos en el mismo paso, mismo error 2 veces, o 2 iteraciones sin progreso. No para typos/fixes obvios. Sin comité en ningún otro caso.

1. Congela en `LOG.md` `## BLOQUEO — <paso>`: 2 intentos + error exacto + pregunta (`¿proceder con A o replanificar a B?`). El "punto bloqueado" = mismo paso + misma causa raíz.
2. **Deep research obligatorio (antes del comité):** investiga en internet el error / stack / API implicada y trae evidencia al comité. Usa `websearch` + docs vía Context7 (`documentation-lookup`) y, si está disponible, la skill `deep-research` (firecrawl/exa). Busca: mensaje de error exacto, issues/changelog, docs oficiales, benchmarks o patrones que resuelvan esto. Guarda en `LOG.md` `## RESEARCH — <paso>`: 3-7 bullets con fuente por bullet (`[fuente]`), sin inventar. Si no hay red o no hay hallazgos, escribe `sin research útil` y sigue degradado.
3. Comité acotado: 4 subagentes en paralelo (Root Cause / Solution Explorer / Benchmark / Architect, 150-300 palabras) + sintetizador secuencial + juez que se moja. Si no hay subagentes, auto-debate por turnos. Dales SIEMPRE el `## RESEARCH` como contexto además del error y archivos. El juez solo decide **proceder / replanificar** con pasos concretos y debe citar qué evidencia del research sostiene el veredicto.
4. Este comité **SÍ puede modificar el plan**: reescribir `PLAN.md` (reordenar, dividir o recortar pasos), reescribir `steps/NN-*.md` afectados y marcar `paralelizable?` de nuevo como hipótesis. Anota en `LOG.md` `## COMITÉ — veredicto N/2: <1 línea> + research usado: <1 línea> + plan modificado: <qué cambió>` y vuelve a FASE 1.
5. Límite por punto: **max 2 comités por cada vez que te quedas bloqueado en el mismo punto**. Tras el 2º por ese punto sin desbloquear → marca ese punto `bloqueado-definitivo`, propone ruta alternativa (re-trazo mayor o recorte de alcance) y sigue con el siguiente paso desbloqueable. Prohibido un 3º comité por el mismo punto.
6. Techo global de seguridad: **max 6 comités por objetivo** (todos de desbloqueo). Al llegar, para y reporta.

## Memoria — límite duro estilo Hermes

Fuente: `memory/current.md` (canónica, `memory.md` es espejo). Límite 2.200 chars. No hay FIFO silencioso: si un `add`/`patch` excede, devuelve error con `current_entries` y exige **un batch** que libere (remove/patch) + añada en la misma operación. Si >80% consolida antes de añadir. Ver `memory/README.md` para protocolo `YYYY-MM-DD_tema` y 2 reads `memory/INDEX.md` → `memory/current.md`.

## Reglas de parada

- Termina SOLO con evidencia de cada criterio de éxito (incluyendo tests + E2E web si aplicó).
- Para a las 15 iteraciones o 6 comités totales sin completar: marca `bloqueado`, reporta qué falta, qué intentaste, veredictos en 1 línea, y propuesta.
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
