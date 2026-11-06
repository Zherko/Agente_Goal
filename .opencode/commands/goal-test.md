---
description: Fuerza modo test GOAL (L0-L3 anti-trampas) aunque el agente pueda activarlo auto - invoca goal-test
---

Invoca la skill `goal-test`: lee `~/.config/opencode/skills/goal-test/SKILL.md` completa y ejecuta su flujo.

Dispara el mismo harness que GOAL auto (core/checks), a demanda y sin lógica duplicada.

Uso: $ARGUMENTS

- `/goal-test` → strict por defecto (L0+L1+L2 bloqueantes, L3 si risk=core)
- `/goal-test --strict` → explícito strict
- `/goal-test --off --reason="..."` → desactiva con traza

Ejecuta `skill({name:"goal-test", args: $ARGUMENTS})`
