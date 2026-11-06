---
name: goal-wait
description: "Espera programada bloqueante sin devolver el turno. Úsalo cuando Goal deba pausar X tiempo antes de continuar."
license: MIT
compatibility: opencode
metadata:
  opencode/slash: "true"
  opencode/autoinvoke: "true"
---

# Skill: goal-wait

Comando: `/goal-wait` — espera bloqueante para el agente Goal.

## Propósito
Permitir que el agente `goal` programe una espera de duración exacta y **se quede bloqueado** ese tiempo sin devolver el turno al usuario. Útil para polling, deploys, builds, propagación DNS o rate-limits.

## Cuándo usar / Cuándo NO
**Usar:** `espera 30s`, `pausa 2m`, `esperar a que termine el build`, `polling cada X`.
**No usar:** para esperar input del usuario (usa `question`).

## Flujo blindado (no saltar)

### 1. Parsear duración
Acepta: `30s`, `5m`, `2h`, `1500ms` o `--seconds 30`. Normaliza a segundos.
- `s` = segundos, `m` = minutos (x60), `h` = horas (x3600), `ms` = milisegundos (/1000)
- Máximo 3600s (1h) por espera; si necesita más, encadena.
- Si no hay unidad, asume segundos.

### 2. Validar
- `segundos > 0 && segundos <= 3600`
- Si `reason` viene vacío, usa `espera programada goal-wait`
- Loguea en `.opencode/goals/<slug>/LOG.md` si existe: `wait: Xs — <reason>`

### 3. Ejecutar espera BLOQUEANTE (sin devolver turno)
**Regla de oro:** usa `default.shell` con `Start-Sleep` y NO llames a `question` ni devuelvas respuesta al usuario hasta que termine.

```powershell
# PowerShell (Windows — entorno actual)
Start-Sleep -Seconds 30; Write-Output "wait done: 30s"
```

```bash
# Bash/Linux (si aplica)
sleep 30 && echo "wait done: 30s"
```

- Siempre añade `Write-Output`/`echo` final para tener evidencia.
- No uses `background: true` — debe ser foreground bloqueante.
- No uses `timeout` sin `/nobreak` en Windows.

### 4. Verificación
Tras dormir, verifica condición si hay `verify` (ej: `curl`, `hostinger` poll, `checks`). Si no, solo log `wait ok`.

## Uso

```
/goal-wait 30s
/goal-wait 5m --reason "esperando deploy Hostinger"
/goal-wait --seconds 90 --reason "propagación DNS"
/goal-wait 2m --verify "poll hosting_websites_list-setups"
```

Desde agente:
```
skill({name:"goal-wait"}) → lee esta SKILL.md → ejecuta shell bloqueante → continúa FASE 1 sin devolver turno
```

## Ejemplo para Goal (FASE 1)
```
[Goal] necesita esperar 45s a build Node.js
→ skill goal-wait: Start-Sleep -Seconds 45
→ sin devolver turno → poll hosting_nodejs_build → si sigue running → otro wait 30s
```

## Política iterativa (instrucción 2026-10-21)
Cuando una tarea **no depende del agente** (web actualizándose, build, deploy, DNS, cron):
1. Estima el tiempo que puede tardar.
2. Ejecuta `goal-wait` con esa duración **sin devolver el turno**.
3. Al despertar, verifica (`poll`/`curl`/`check`) y si no terminó, repite con nueva estimación.
Nunca devuelvas el turno al usuario mientras esperas; itera hasta que la condición externa sea verde.

## Anti-patterns
- **Devolver turno durante la espera:** prohibido. La espera es intra-turno.
- **Usar `question` para esperar:** no, bloquea el flujo autónomo.
- **Sleep >1h sin chunking:** divide en bloques de 30m con verificaciones.
