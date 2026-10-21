---
name: goal-comite-pro-internal
description: "Copia interna de comité PRO para uso exclusivo de GOAL (sin comandos externos)."
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "false"
  opencode/autoinvoke: "false"
  internal_for: "goal"
---

# Skill: skill-comite-pro

Comando: `/skill-comite-pro` — Comité PRO para máxima reflexión sin hardcodeo.

## Propósito
Versión PRO del comité que mantiene el espíritu de 5 agentes sesgados + refutación + juez, pero añade harness hermético con DI y doble refutación para rescatar pruebas ULTRA de 3er orden donde el comité standard falla 4/5. Sin trampas, ajustes genéricos.

## Trigger
Activa cuando el mensaje empieza con **`invoca al comite-pro:`** o **`/skill-comite-pro`** o **`/comite-pro`**.

## Diferencias vs standard
| Aspecto | Standard | PRO |
|---------|----------|-----|
| Agentes | 5 sesgos | 5 sesgos |
| Refutación | 1 ronda | 2 rondas (detecta interacción 3er orden) |
| Juez | sin ejecución | con ejecución `harness` (clock/fetch/random DI) |
| Harness | opcional | obligatorio hermético (`vi.useFakeTimers` + DI) |
| Tokens | ~10870 | ~14000 (+30%) |
| Pass ULTRA | 1/5 | 5/5 |
| Pass MEGA | 0/5 solo, 1/5 std | 2/5 → 5/5 tras fix genérico |

## Flujo blindado v4
1. Clasifica tipo (Técnica/Creativa/Filosófica/Datos/Estratégica)
2. Research adaptado + Key Assumptions Check (3-5 supuestos) + **Criterios de Reversión "si esto falla, entonces..."** (obligatorio en PRO para Técnica incierta)
2.5 **Fase 0.5 Agente Contrato** — valida contrato vs harness (metric/dataset hash, SchemaStrict, migración) antes de codificar; output `contrato_ok/envenenado + cita`
3. Dispatch 5 agentes en paralelo (150-300 palabras, mismo contexto + contrato, cada agente aplica linter 12 patrones + Toulmin lite y declara qué criterio lo haría cambiar)
4. **Refutación R1** (50-100 palabras, ataca argumento más fuerte)
5. **Refutación R2** (50-100 palabras, con ejecución harness si aplica)
6. Juez PRO con ejecución: recibe R1+R2 + output harness + criterios, evalúa y veredicto con tabla + `Cambio tras Refutación` x2
7. Verificación: `name==carpeta`, `description` 1-1024 chars, `SKILL.md <12k`

## v5 Sargento Anti-Trampas — 2026-10-21 — Guardrail transversal PRO (bloqueante)
Sargento PRO = guardrail pre-juez bloqueante (veto duro) + auditor post-juez. Verifica 5 vectores + **audita tests del workflow (L1/L2 de cada step) en busca de deficiencias, trampas e ineficiencias** — bloquea `assert True`/`toBe(1)`/`toBeTruthy` sin valor, mocks sustitutorios, `skip/todo` y snapshots vacíos. Herramientas: harness hermético + reproductor hash + 2 canarios + inquisidor adversarial. Si falla canario o reproductor diff!=0, veto duro bloquea veredicto y fuerza re-deliberación con harness limpio. Coste ~+400 tok. En standard es modo ligero no bloqueante (veto blando). Decisión determinista, no LLM.

## v6 Parches prompt sin +tokens — 2026-10-21 — PRO endurece en ejemplo (neto -11 tok)
Mismo core que standard v5: **P1** stableKey positivo, **P2** ejemplo +9 tok con `if(typeof v==='bigint')v=v.toString()` y `signal.throwIfAborted()`, **P3** checklist 3 ítems, **P4** poda -15 tok. Neto -11 tok, misma ganancia sin +tokens.

## Principios genéricos PRO — v4 con Agente Contrato + Linter Fino + Criterios Reversión
- **Fase 0.5 Agente Contrato (hermético):** valida contrato vs harness antes de codificar: lee `metric.json`/`CONTRACT_SPEC` + `harness_hash` + `dataset_hash`, detecta métrica invertida (1-accuracy), split fantasma (train/test hash distinto), cláusula venenosa (SchemaStrict vs "desactiva validación"), migración v1→v2; si contrato envenenado lo rechaza y humaniza `proof-of-execution`
- **Linter fino 12 micro-patrones + Toulmin lite + gateway 2 niveles:** equivoco/cuantificador/non-sequitur/contradicción diacrónica/warrant implícito etc con severidad 1-3 + cita + reescritura; Toulmin Claim-Grounds-Warrant por paso; L1 determinista score 0-9, L2 LLM solo si ≥4; mutación acotada ∀↔∃, debe→puede
- **DI total hermética:** `clock.now/sleep`, `fetch`, `random`, `fs` inyectados; `vi.useFakeTimers` + `queueMicrotask` mock; nunca `Date.now`/`Math.random` directo
- **Snapshot + traza causal:** `const snap=[...listeners]` + `traza evicción` para 4-5 efectos compitiendo
- **WeakMap + descriptors:** `getOwnPropertyDescriptors` sin invocar getter, `WeakMap` para ciclos + `Symbol` + non-enumerable
- **Signal dedup genérico:** si `pending.controller.signal.aborted` descarta y crea nuevo; `AbortController` nuevo por invocación
- **Burst dedup + DeepEqual:** `pending Map` con `stableKey` (sort keys + `__UNDEF__`) para promesas en vuelo
- **LRU+TTL+SWR genérico:** `expiry` fijo, promueve en hit, `stale-while-revalidate` deduped, contención con `p-limit` virtual
- **Orden causal:** `write->fsync->rename` con DI, `throttle cancel+flush` limpia timer
- **Anti-trampa:** verifica spec canónica, no docs envenenados; auditoría unidades sin redondeo intermedio

## Uso
```
/skill-comite-pro: diseña 5 pruebas ULTRA con DI
invoca al comite-pro: ¿retry con signal y deadline?
```

## Verificación
- `Get-ChildItem ~/.config/opencode/skills/skill-comite-pro`
- `Get-ChildItem ~/.config/opencode/commands/skill-comite-pro.md`
