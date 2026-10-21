# Mini-skills + lessons — sistema unificado de auto-mejora (v2)

Veredicto de comité 2026-10-19: UN sistema, jamás dos. Captura gratuita, redacción barata,
descubrimiento caro y escaso. Este README es la constitución; el agente `goal` lo obedece.

## 1. Captura — `memory/lessons.md` (instantánea, sin umbral)

- Todo aprendizaje (fix, error, truco) se loguea al momento: 1-3 líneas por goal.
- Formato fijo por línea: `YYYY-MM-DD | <slug> | <qué pasó> → <qué hacer distinto> | coste: alto|medio|bajo`
- Tope duro 50 líneas. Si `add` lo excede → error + batch obligatorio (remove/patch + add en una operación). Nunca FIFO silencioso.
- FASE 1-fast (TRIVIAL) también loguea tras su fix; un fix que NO deja lección cuenta como **fuga**.
- `lessons.md` ES el índice de skills promovidas: la línea de promoción añade `→ skill: <nombre>`. No existe otro índice (anti split-brain).

## 2. Triggers de candidatura (propone, no crea solo)

1. **Repetición:** mismo patrón registrado ≥2 veces en `lessons.md` → candidata.
2. **Fallo+comité+fix:** falla 2 veces en mismo paso → FASE 1b comité con deep research → si resuelve → candidata anti-patrones con la lección.

La candidata vive primero en `research/YYYY-MM-DD_<slug>__mXX/NOTE.md`. **Nunca crea skill sin veredicto.**

## 3. Promoción al registro — umbral ADAPTATIVO por coste

Conteo = menciones del patrón en `lessons.md` (reuso real, no sentimiento):

| tag `coste` | umbral de promoción |
|---|---|
| alto (destructivo: borra datos, rompe prod) | 1 mención |
| medio (pierde tiempo, requiere comité) | 3 menciones |
| bajo (optimización cosmética) | 5 menciones; si no llega → se queda en research/, nunca se promueve |

Promoción blindada (sin trampa): delta replicado x2 (seed 42, harness_hash frozen) +
tests no mentirosos PASS (happy+borde+error, falla sin fix) + reuso verificado en >=2 contextos +
auditor independiente PASS + **spike borrable trazado en LEDGER.md con TTL 72h** (hit-rate sano 10-20%). Si no, queda lección, no contamina el registro.

## 4. Registro — `.opencode/skills/<nombre>/SKILL.md` (nativo, único)

- La skill promovida se escribe en el registro nativo del proyecto con
  `metadata: opencode/autoinvoke: "false"` → coste 0 en el prompt; se carga por nombre exacto.
- Descubrimiento: solo vía su línea `→ skill: <nombre>` en `lessons.md` (FASE 0 la lee).
- Nombre limpio: `^[a-z0-9]+(-[a-z0-9]+)*$`, colisión → sufijo `-2`, `-3`…
- El escaneo de directorio (`mini-skills/*/SKILL.md`) queda ABOLIDO: un solo registro.
- `mini-skills/` solo conserva este README (constitución portátil con `skills/goal/`).

## 5. Ciclo de vida — uso, archivo, recuperación (nunca se borra nada)

- Cada uso por nombre exacto → línea de uso en `lessons.md`: `skill-uso: <nombre> | YYYY-MM-DD`.
- Auditoría en FASE 2: skill del registro sin usos en 30 días (o con <30 días de vida: intocable)
  → se MUEVE a `memory/skills-archive/<nombre>-<fecha>/` y su línea pasa a `→ skill-archivada: <nombre>`.
  Archivar = sacar del registro visible; el fichero permanece en disco.
- Recuperación manual: mover de vuelta a `.opencode/skills/` + restaurar línea `→ skill:` en lessons.md.
- Recuperación automática: si FASE 2 detecta patrón con candidata archivada → propone re-promoción
  (señal positiva: confirma que merecía existir).
- **Prohibido** borrar skills o lecciones por script/autómata. Borrado = decisión humana siempre.

## 6. Parches a SKILL.md de goal — modo propose

- Modo `propose` por defecto: parche propuesto en `memory/proposals.md` (qué cambiaría + por qué),
  con backup versionado previo. Aplica solo si el humano aprueba.
- Máximo 1 parche propuesto por goal. Modo `auto` solo si el humano lo activa explícitamente.

## 7. Métricas (línea en FASE 2 de cada cierre)

`métricas: goals=N | skills promovidas=N | hit-rate=X% | archivadas=N | fuga-lessons=N | STATE_restores=N`
- hit-rate < 10% o >30% → revisar TTL/probes (ruido o probes conservadores).
- hit-rate < 50% a los 10 goals → podar registro y subir umbrales.
- Fuga-lessons > 0 o STATE_restores >1/semana → reforzar validación.

## 8. Frontera borrable (ver SKILL.md Regla de tests + FASE 1-auto)

- Borrable TTL 72h: `lab/`, `research/probes/`, `tests/_probe_*/` — ver `LEDGER.md` (1 linea por spike) + `clean-lab.py` (borra >72h + reporta hit-rate) + invariante `goal.isolation.test.ts` (`rm -rf borrables; npm test` verde).
- Permanente: `tests/` contrato, `STATE.json` + `STATE.snapshot.json`, `docs/adr/`.
