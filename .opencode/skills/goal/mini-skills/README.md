# Mini-skills — trigger y promoción (portable)

Viven en `skills/goal/mini-skills/YYYY-MM-DD_<nombre>__mXX/SKILL.md` para portar con `skills/goal/` + `agents/goal.md`.

## Triggers (propone, no crea solo)
1. **Repetición:** mismo patrón ≥2 veces (ej: api-crud x2) → propone mini-skill
2. **Fallo+comité+fix:** falla 2 veces en mismo paso → FASE 1b comité (con deep research) → si resuelve → propone mini-skill anti-patrones con la lección

Nunca crea sin veredicto. Candidata queda en `research/YYYY-MM-DD_<slug>__mXX/NOTE.md` primero.

## Promoción (blindada, no trampa)
Solo a `mini-skills/` si:
- delta replicado x2 (seed 42, harness_hash frozen)
- tests no mentirosos PASS (happy+borde+error, falla sin fix)
- reuso verificado (T3 usa marker template, no duplica)
- auditor independiente PASS (compartimentado en lab/review/)

Si no, queda en research/ como lección, no contamina skills.

## Reuso
Próximo goal con mismo patrón lee `mini-skills/*/SKILL.md` y aplica template (ahorro ~80% medido en lab api-crud).
