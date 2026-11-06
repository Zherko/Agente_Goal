# Agente_Goal â€” Orquestador todo-terreno para opencode

> **1 objetivo â†’ plan seccional â†’ runtime soberano â†’ comitÃ© solo si se atranca.** Portable en 2 carpetas.

`Goal` no es un plugin: es **skill + agente** con memoria dura, research determinista, paralelizaciÃ³n calibrada y mini-skills auto-propuestas.

## QuÃ© trae

| Carpeta en repo | Se instala en | QuÃ© es |
|---|---|---|
| `.opencode/agents/goal.md` | `~/.config/opencode/agents/goal.md` | Picker (router ligero <1k tok, personalidad 7/10/10/2) |
| `.opencode/skills/goal/` | `~/.config/opencode/skills/goal/` | Cerebro (SKILL.md + research + memory + mini-skills + ENJAMBRE-RULES) |

Incluye:
- **Memoria lÃ­mite duro 2.200 chars** estilo Hermes (no FIFO silencioso, exige batch si se llena) â€” hallable 2 reads `memory/INDEX.md â†’ current.md`
- **Research determinista** `--research` con `early_stop 2`, `harness_hash` frozen, protocolo `YYYY-MM-DD_<investigaciÃ³n>__mXX/` â€” 5 ciclos max
- **ParalelizaciÃ³n calibrada** desde tu Enjambre (overhead 62k, `block.json` ledger, writer-batch -77%, umbrales TRIVIAL â‰¤500 / SMALL â‰¤10k / LARGE >10k)
- **Mini-skills** auto-propuestas: por repeticiÃ³n x2 o por `fallo â†’ comitÃ© â†’ fix` â†’ promociÃ³n solo con tests no mentirosos + replica x2 + auditor


> **Nuevo 2026-11-06:** Karpathy ya vive dentro de Goal (4 principios + micro-contrato 3L) y Goal habla en humano: max 60 palabras / 5 lineas. Dependencias incluidas: .opencode/skills/karpathy-guidelines/ + skills/goal-*/ + agents/team.md

## InstalaciÃ³n (otro opencode, 1 comando)

### OpciÃ³n A â€” instalador (recomendado)
```powershell
git clone https://github.com/Zherko/Agente_Goal.git
.\Agente_Goal\install.ps1
# o: .\install.ps1 -Force
```
Copia `.opencode/agents/goal.md` â†’ `~/.config/opencode/agents/` y `.opencode/skills/goal/` â†’ `~/.config/opencode/skills/goal/`. No pide confirmaciÃ³n si ya existe con `-Force`.

### OpciÃ³n B â€” manual
```powershell
Copy-Item .opencode\agents\goal.md $env:USERPROFILE\.config\opencode\agents\goal.md -Force
Copy-Item -Recurse .opencode\skills\goal $env:USERPROFILE\.config\opencode\skills\goal -Force
```

Verifica:
```powershell
opencode --agent Goal "hola â€” verifica instalaciÃ³n"
# o slash:
/goal "aÃ±adir auth email a Project/src/auth, con tests"
```

## Uso

```powershell
/goal "aÃ±adir auth email a Project/src/auth, con tests"
/goal "mejorar $/K churn 10% en packages/core" --research
/goal --resume <slug>
```

Flujo: `FASE -1 grill me` â†’ `FASE 0 clasifica+check-first hash` â†’ `FASE 0b plan con agente plan (edit:deny)` â†’ `FASE 1.R research opt-in` â†’ `FASE 1 runtime (disjunciÃ³n+block.json)` â†’ `FASE 1b comitÃ© solo si 2 fallos`

## Estructura instalada

```
~/.config/opencode/
  agents/goal.md
  skills/goal/
    SKILL.md
    agent.md
    ENJAMBRE-RULES.md
    block.json / block.schema.json
    memory/current.md + INDEX.md + README.md
    research/controller.md + template/NOTE.md
    mini-skills/README.md
```

Portable: copia esas 2 rutas y tienes el agente completo.

## Desarrollo / Lab

Lab aislado con harness determinista seed 42, tests no mentirosos y auditor compartimentado en `C:/Users/user/Documents/lab-opencode/runs/2026-10-18-mini-skills/` (no toca skill real).

## Licencia

MIT â€” ver `LICENSE` si se aÃ±ade.
