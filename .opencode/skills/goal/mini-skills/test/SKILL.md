---
name: goal-test
description: "Lanza tests robustos de GOAL (L0-L3 anti-trampas). Usa /goal_test o /goal_test --strict/--off"
license: MIT
compatibility: opencode
metadata:
  internal_for: "goal"
  opencode/slash: "false"
  opencode/autoinvoke: "false"
---

# /goal_test — Tests GOAL robustos

Dispara el mismo harness que GOAL auto, a demanda.

## Uso
- `/goal_test` → strict por defecto (L0+L1+L2 bloqueantes, L3 si risk=core)
- `/goal_test --strict` → igual, explícito
- `/goal_test --off --reason="..."` → desactiva con traza

Ambos caminos usan `core/checks` — no hay lógica duplicada con GOAL auto.

Ejecuta: `npx vitest run tests/harness/plan_long --reporter=verbose` + checks L0-L3 según `GOAL-TEST-CONTRACT`.
Si falta `diagnosis/diff.patch` en fail → run inválido.
