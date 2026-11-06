---
updated: 2026-11-02
version: 3
limit: 2200
limit_user: 1375
mode: hard
---

# Goal — Memoria usuario (curada, límite duro estilo Hermes)
# Reglas: 2.200 chars; un add que exceda exige batch remove/patch+add. Ver memory/README.md

## Preferencias (max 35)
- [2026-10-17] respuestas breves 1-4 líneas, 1 tecnicismo; `detalla` rompe el límite
- [2026-10-21] si la tarea externa no depende del agente (web/build/deploy), goal-wait sin devolver turno

## Hechos (max 35)
- [2026-11-02] Goal: proof en research/<exp>/traces/<hash>.r1/.r2.proof; valida logger/index.js:validateProof; lab/ prohibido
- [2026-11-02] skill-init: AGENTS.md con ## Comandos + .opencode/plans/ + improvements/ROOM.md + research/.harness.lock
- [2026-11-01] Backtest: DD diario vs equity de inicio de día, DD total vs depósito; abortar no cierra posiciones
- [2026-10-31] MQL5: LightGBM CPU/OpenCL fp64 = Python (Δ=0); ranking lambdarank ndcg 0.7438 vs 0.7385 LGBM; corpus 12/12
- [2026-10-29] repo privado Zherko/Agente-contenido (reels), out/ fuera de git; UI juego: alternativa 02b
- [2026-10-23] MCP metaeditor/terminal puede no verse en sesión; sin él el tester exige cerrar terminal64
- [2026-10-17] GO plan activo, Jev descartado; Goal global = skills/goal + agents/goal + /skill_goal

## Anti-patrones (max 20)
- [2026-10-17] no usar Jev ni Console fuera de GO
- [2026-10-17] no auto-inyectar memoria completa en CONTEXT.md

## Pendientes (max 10)
- [2026-11-03] /goal = flujo completo por defecto; `--fast` solo explicito; /goal-full retirado
- [2026-11-02] Goal: no le falta inteligencia, le falta parar y anotar (11/15 sin leccion); cierre opt-in
- [2026-11-02] compactar memoria cada ~5 goals (sin hook automático)
