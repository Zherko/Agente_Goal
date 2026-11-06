# Agente Goal

Orquestador de objetivos para **opencode**: plan seccional, ejecución con tests que no mienten, comités solo cuando se atasca, y un modo de **auto-research** que itera contra una métrica hasta mejorarla o rendirse con evidencia.

## Qué instala

| Pieza | Qué hace |
| --- | --- |
| `agents/goal.md` | Agente Goal (picker) |
| `agents/team.md` | Clon portable de Goal |
| `skills/goal/` | Núcleo: fases, plan, runtime, tests, investigación, tablero |
| `skills/goal-*` | Dependencias (plan, discovery, comité, research, test, wait) |
| `skills/karpathy-guidelines` | Los 4 principios que Goal aplica |
| `commands/goal*.md` | Atajos `/goal`, `/goal-research`, `/goal-autoresearch`, `/goal-dashboard`, `/goal-test`, `/goal-wait`, `/goal-atributos` |

## Instalar

```powershell
git clone https://github.com/Zherko/Agente_Goal
cd Agente_Goal
.\install.ps1
```

Copia agentes, skills y comandos a `~/.config/opencode/`. **No pisa tu memoria**: si ya tienes `memory.md`, `current.md`, `lessons.md` o `INDEX.md`, se conservan.

Requisitos: opencode y, para el tablero, `python` (3.9+).

## Uso

```powershell
/goal "añadir auth por email en src/auth, con tests"
/goal-research "bajar p95 de la API un 10%"
/goal-autoresearch "bajar p95 de la API un 10%"
/goal-dashboard
```

### `/goal` (flujo completo)
Plan seccional con el agente `plan`, tabla de pasos con verificación, tests falsables (fallan sin el cambio, pasan con él), y comité cuando hay dos fallos seguidos.

### `/goal-research` (investigación normal)
Hasta 5 ciclos contra una métrica con harness congelado. Guarda cada experimento en `research/YYYY-MM-DD-nombre/` con `NOTE.md`, `metric.json` y pruebas de ejecución. Se rinde a los 3 fallos seguidos.

### `/goal-autoresearch` (investigación profunda)
Igual, pero con presupuesto mayor: comité cada 2 fallos hasta **10 comités seguidos**, que vuelven a 0 al conseguir una mejora replicada. El 10.º comité es **PRO** (doble refutación). Cada prueba escribe un cuaderno de 6 apartados:

```
## Hipótesis
## Protocolo (prueba hecha)
## Resultado (métrica + proof)
## Hallazgo (positivo / negativo)
## Interpretación
## Siguiente prueba
```

Además mantiene `research/LEARNINGS.md`: la base de conocimiento acumulada (máx. 3 líneas por experimento, con la pista que guía la siguiente prueba).

Antes de empezar escribe `research/CHANGE_SPACE.md` con lo que se puede tocar y lo que no (el medidor y los tests, nunca). Si hay muestra suficiente (≥50 casos) aparta un **20%** en `research/holdout/` que no se usa para mejorar: solo se mide al validar una mejora o al cerrar. Mejorar solo en entrenamiento y no en el examen es sobreajuste y no se promueve.

### `/goal-dashboard` (tablero)
Arranca la Torre de Control en `http://127.0.0.1:3010`:

- **Objetivos** — contadores, evolución de consumo y tabla con nivel y coste.
- **Auto-research** — lista de investigaciones; al entrar, gráfica de progreso arriba, la ruta de hipótesis, las versiones guardadas y las pruebas debajo; al abrir una prueba, su cuaderno completo.

Se regenera en cada visita: puedes dejarlo abierto mientras Goal trabaja. Sin dependencias (solo Python estándar).

## Dónde vive el trabajo

```
.opencode/goals/<slug>/        plan, log, estado, diagnóstico
research/
  _index.md                    tabla de pruebas (fecha · veredicto · hallazgo)
  LEARNINGS.md                 conocimiento acumulado, 3 líneas por prueba
  ROADMAP.md                   camino recorrido · vivo · descartado · siguiente
  CHANGE_SPACE.md              qué se puede tocar y qué no
  holdout/holdout.json         20% reservado, fuera de muestra
  VERSIONS.md                  versiones del archivo investigado
  BEST.md                      apuntador a la mejor versión
  versions/v000-original/      el archivo tal como estaba, intacto
  versions/vNNN-<prueba>/      copia exacta en cada mejora (archivo + meta.json)
  YYYY-MM-DD-<prueba>/         NOTE.md · metric.json · traces/*.proof · artifacts/
```

Nada se pierde: cada prueba conserva su cuaderno y su parche, y cada mejora deja una copia completa del archivo. Al cerrar, si el resultado final es peor que la mejor versión, se restaura esa.

## Principios

1. Piensa antes de codificar.
2. Lo simple primero.
3. Cambios quirúrgicos.
4. Verifica con prueba real, siempre.
