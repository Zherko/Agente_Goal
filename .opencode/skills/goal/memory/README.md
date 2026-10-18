# Memoria Goal — carpeta ordenada (límite duro estilo Hermes)

Estructura migrada ( `memory.md` en raíz es espejo → fuente real `memory/current.md`):

```
skills/goal/memory/
  README.md           <- este archivo (protocolo)
  current.md          <- memoria viva (espejo de ../memory.md, fuente de verdad)
  INDEX.md            <- índice hallable 2 reads: fecha | tema | líneas | link
  2026-10-17_baseline.md  <- snapshot diario opcional
  archive/
    2026-10-18_archive.md <- expulsados por FIFO (antes memory_archive.md)
```

## Protocolo de nombre — memorias
`YYYY-MM-DD_<tema-kebab>.md` — fecha = orden lexicográfico, tema = slug estable

Ejemplos:
- `2026-10-18_respuestas-breves.md`
- `2026-10-18_preferencias-go.md`
- `2026-10-19_hechos-panel-control.md`

Si solo hay una memoria viva, se usa `current.md` (siempre). Los snapshots son opcionales para auditoría.

## Capacidad — límite duro (copiado de Hermes)
- `current.md` = 2.200 chars (~800 tokens, 8-15 entradas). `USER.md` futuro = 1.375 chars si se separa.
- **No hay FIFO silencioso.** Si un `add` excede el límite, la tool devuelve error:
  ```
  { success:false, error:"Memory at 2100/2200 chars; adding 250 chars would exceed by 150. Retry as ONE batch that removes/patches stale entries to free >=150 chars AND adds entry" }
  ```
  El agente debe reemitir **un batch** que libere (remove/patch) + añada en la misma operación. El límite se chequea solo al resultado final.
- Cuando >80% (1.760 chars) consolida antes de añadir: fusiona 3 entradas relacionadas en 1 densa.

## Uso
- `read memory/current.md` = READ 1 (foto congelada al iniciar sesión)
- `read memory/INDEX.md` = READ 1 alternativo hallable 2 reads
