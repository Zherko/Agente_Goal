# Agente_Goal — Orquestador todo-terreno para opencode

> **1 objetivo → plan seccional → runtime soberano → comité solo si se atranca.** Portable en 2 carpetas.

`Goal` no es un plugin: es **skill + agente** con memoria dura, research determinista, paralelización calibrada y mini-skills auto-propuestas.

## Qué trae

| Carpeta en repo | Se instala en | Qué es |
|---|---|---|
| `.opencode/agents/goal.md` | `~/.config/opencode/agents/goal.md` | Picker (router ligero <1k tok, personalidad 7/10/10/2) |
| `.opencode/skills/goal/` | `~/.config/opencode/skills/goal/` | Cerebro (SKILL.md + research + memory + mini-skills + ENJAMBRE-RULES) |

Incluye:
- **Memoria límite duro 2.200 chars** estilo Hermes (no FIFO silencioso, exige batch si se llena) — hallable 2 reads `memory/INDEX.md → current.md`
- **Research determinista** `--research` con `early_stop 2`, `harness_hash` frozen, protocolo `YYYY-MM-DD_<investigación>__mXX/` — 5 ciclos max
- **Paralelización calibrada** desde tu Enjambre (overhead 62k, `block.json` ledger, writer-batch -77%, umbrales TRIVIAL ≤500 / SMALL ≤10k / LARGE >10k)
- **Mini-skills** auto-propuestas: por repetición x2 o por `fallo → comité → fix` → promoción solo con tests no mentirosos + replica x2 + auditor

## Instalación (otro opencode, 1 comando)

### Opción A — instalador (recomendado)
```powershell
git clone https://github.com/Zherko/Agente_Goal.git
.\Agente_Goal\install.ps1
# o: .\install.ps1 -Force
```
Copia `.opencode/agents/goal.md` → `~/.config/opencode/agents/` y `.opencode/skills/goal/` → `~/.config/opencode/skills/goal/`. No pide confirmación si ya existe con `-Force`.

### Opción B — manual
```powershell
Copy-Item .opencode\agents\goal.md $env:USERPROFILE\.config\opencode\agents\goal.md -Force
Copy-Item -Recurse .opencode\skills\goal $env:USERPROFILE\.config\opencode\skills\goal -Force
```

Verifica:
```powershell
opencode --agent Goal "hola — verifica instalación"
# o slash:
/goal "añadir auth email a Project/src/auth, con tests"
```

## Uso

```powershell
/goal "añadir auth email a Project/src/auth, con tests"
/goal "mejorar $/K churn 10% en packages/core" --research
/goal --resume <slug>
```

Flujo: `FASE -1 grill me` → `FASE 0 clasifica+check-first hash` → `FASE 0b plan con agente plan (edit:deny)` → `FASE 1.R research opt-in` → `FASE 1 runtime (disjunción+block.json)` → `FASE 1b comité solo si 2 fallos`

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

MIT — ver `LICENSE` si se añade.
