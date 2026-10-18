# ENJAMBRE-RULES — reglas de paralelización para Goal

> Fuente: Agente_enjambre (Zherko) + benchmark 6 proy. Integrado en Goal como skill, no agente externo.

## Regla 0 — Clasificador 3 niveles (overhead 62k/sesión)

| Nivel | Umbral | Acción |
| TRIVIAL | ≤500 tok o 1 archivo o <30s razonamiento | Directo SIN subagentes, vía rápida FASE 1-fast |
| SMALL | ≤10k tok trabajo real (≤5k ideal), 3-5 archivos simples | Directo SIN subagentes (orquestador) |
| LARGE | >10k tok o multi-archivo complejo | Autoriza verificar disjunción → posible paralelo |

Cada subagente paga ~62k base (+15k/archivo). En trivial overhead 136:1.

## Regla 1 — Desfragmentar solo lo desfragmentable

Solo paralelo si TODAS:
1. Interfaces estables entre subtareas
2. Conjuntos de archivos disjuntos (validar `block.json` antes de lanzar)
3. I/O-bound independientes (explorar/leer/buscar/redactar). CPU del modelo NO paraleliza.

Si solape → secuencial. Ledger en `block.json` (claims informativos, no lock).

## Regla 2 — Agentes selectivos

- 1 paso → directo
- 3+ docs disjuntos → writer-batch 1 sesión (1 writer hace N archivos, -77% vs N workers)
- ≥2 pasos disjuntos + >10k tok → subagentes en paralelo con mensaje mínimo `lee X, escribe Y`
- Nunca -pure overhead por <10k tok

## Regla 3 — block.json ledger

```json
{ "run":"<slug>", "workspaceRoot":"<ruta>", "claims":[{"agent":"goal-worker","subtask":"paso-2","files":["src/pagos/**"],"status":"active|done"}] }
```

Lo escribe orquestador, workers solo leen.

## Regla 4 — Medir (tabla evolución)

Cada objetivo LARGE cierra con fila en `LOG.md`:
`| Versión | Coste $ | Tokens in+out | Tiempo s | vs basal |` — referencia `lab/TABLA-EVOLUCION.md` de enjambre. Sin tabla no hay conclusión de ahorro.

## Ahorros validados (enjambre v1.1, 6 proy)

- Promedio router: -15.5% tokens / -4.7% tiempo / -13% coste
- Pico P6 1461 lin: -48.2% tokens
- Pico ideal 6 proy: -25.2% tokens / -41.2% tiempo
- Techo: ~25-30% tokens, ~40% tiempo. Writer-batch es la clave.
