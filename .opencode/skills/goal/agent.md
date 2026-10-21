# agent.md — Goal (global)

## Vision — Goal (global)
Orquestador de objetivos con plan seccional y runtime soberano. Disponible como `/goal` en cualquier proyecto. **Compartimentado:** este archivo es router ligero (~20 líneas); el workflow completo vive en `SKILL.md:1` sin pérdida.

## Arquitectura blindada
- **Router ligero:** `agent.md:1` (este archivo, <1k tokens) — solo rol + blindajes + dispatch
- **Fuente única:** `SKILL.md:1` (fases -1→0→0b→1.R→1→1b) + `research/controller.md` para auto-research + `ENJAMBRE-RULES.md` para paralelización — tests no mentirosos, output cerrado
- **Lazy load obligatorio:** al iniciar SIEMPRE `read SKILL.md` completo antes de actuar. Prohibido decidir sin leerlo.
- **Memoria en disco:** `.opencode/goals/<slug>/` + `INDEX.md` — no en chat; research hallable en 2 reads: `research/INDEX.md` → `research/YYYY-MM-DD_<slug>/NOTE.md`
- **Plan aislado:** delega partición a agente `plan` nativo (`edit:deny`), nunca planifica escribiendo código
- **Comité solo al atrancarse:** `SKILL.md:81` — max 2 por punto, 6 global, con deep research + Key Assumptions Check + 5 agentes paralelos + refutación cruzada + juez con criterios de reversión (alineado `/skill-comite`); research: deep research inicial + comité arranque opcional, luego early-stop 2 fallos

## Flujo resumido (detalle en SKILL.md + research/controller.md)
1. FASE -1 grill me si ambiguo (puede proponer `research.enabled` si huele métrica) → 2. FASE 0 slug+clasifica+check-first por hash → 3. FASE 0b plan con `plan` (+ research harness si enabled) → 3b. FASE 1.R deep research inicial + comité arranque + loop hallable 2 reads (opt-in `--research`) → 4. FASE 1 runtime disyunción+dispatch+tests → 5. FASE 1b desbloqueo con comité si 2 fallos

## Blindajes core
- TRIVIAL va vía rápida sin PLAN ni comité (`SKILL.md:24` + `ENJAMBRE-RULES.md:0` ≤500 tok)
- `paralelizable?` es hipótesis, runtime verifica disjunción + `block.json` ledger (`SKILL.md:42`, `block.schema.json`)
- Writer-batch: 3+ docs disjuntos → 1 sesión (-77% vs N workers) (`ENJAMBRE-RULES.md:2`)
- Tests no mentirosos obligatorios, Playwright si UI (`SKILL.md:72`)
- Nunca borrar `.opencode/goals/<slug>/`, archivar a `archive/`

## Uso
```
/goal "añadir auth email a Project/src/auth, con tests"
/goal "mejorar $/K churn 10% en packages/core" --research
/goal --resume <slug>
/goal "optimizar LCP blog" --research  # activa FASE 1.R: deep research → comité arranque → loop fecha-experimento
```

## Estado
Router <1k tokens, SKILL.md 115 líneas intactas, global disponible. Ver `SKILL.md:1` para workflow completo.
