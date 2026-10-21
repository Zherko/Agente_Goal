---
name: goal-committee
description: "Desbloquea un punto atascado (2 fallos mismo paso) con deep research + 5 agentes + refutacion + juez. Usalo desde Goal FASE 1b o pre-comite A_conditional."
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "false"
  opencode/autoinvoke: "false"
---

## Cuando
Solo si 2 fallos en mismo punto (mismo paso + misma causa) o `pre_comite=true` (p>0.36) en FASE 0b.

## Flujo
1. Congela `LOG.md` `## BLOQUEO — <paso>`: 2 intentos + error exacto + pregunta `¿proceder con A o replanificar a B?`.
2. Deep research obligatorio: websearch + Context7 sobre error/stack/API, 3-7 bullets con fuente `[fuente]` en `LOG.md ## RESEARCH`. Si sin red, `sin research útil`.
3. Key Assumptions Check: lista 3-5 supuestos `Si es falso → ...` tag `[Verificable]/[No verificable]` en `LOG.md ## ASSUMPTIONS`.
4. Comité acotado 5 subagentes en paralelo (Root Cause / Solution Explorer / Benchmark / Architect / Integration, 150-300 palabras) + refutación cruzada 50-100 palabras + juez con tabla Postura|Fortaleza|Debilidad|Cambio + Consensos/Conflictos + Refutaciones efectivas + veredicto proceder/replanificar con Criterios de Reversión citando research.
5. Puede modificar plan: reescribir `PLAN.md` y `steps/NN-*.md` y recalcular `paralelizable?`. Anota `## COMITÉ — veredicto N/2: ...` y vuelve a FASE 1.
6. Límite por punto: max 2 comités; tras 2º sin desbloquear → `bloqueado-definitivo` y sigue con siguiente paso. Techo global 60 por objetivo.
