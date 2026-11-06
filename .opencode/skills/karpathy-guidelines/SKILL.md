---
name: karpathy-guidelines
description: "Principios de Andrej Karpathy para reducir errores tipicos de LLM al codificar: pensar antes de codificar, simplicidad primero, cambios quirurgicos y ejecucion orientada a objetivos con criterios verificables."
---

# Karpathy Guidelines — para OpenCode

Adapta `CLAUDE.md` original de multica-ai/andrej-karpathy-skills a OpenCode (generico y por proyecto).

**Tradeoff:** Prioriza cautela sobre velocidad. Para tareas triviales usa criterio.

## 1. Think Before Coding

- Expresa supuestos explicitamente. Si dudas, pregunta.
- Si hay varias interpretaciones, presentalas — no elijas en silencio.
- Si hay un enfoque mas simple, dilo. Cuestiona cuando toque.
- Si algo es confuso, para. Nombra que no entiendes y pide aclaracion.

## 2. Simplicity First

- Minimo codigo que resuelve el problema. Nada especulativo.
- Sin features no pedidas, sin abstracciones de un solo uso.
- Sin flexibilidad/configurabilidad no solicitada.
- Sin manejo de errores para escenarios imposibles.
- Si 200 lineas podrian ser 50, reescribe.

Test: ¿diria un senior que esta sobrecomplicado? Si si, simplifica.

## 3. Surgical Changes

Al editar codigo existente:
- No mejores codigo, comentarios o formato adyacente.
- No refactorizes lo que no esta roto.
- Respeta el estilo existente aunque lo harias distinto.
- Si ves dead code no relacionado, mencionalo — no lo borres.

Si tus cambios dejan huerfanos:
- Elimina imports/variables/funciones que TU cambio dejo sin uso.
- No elimines dead code preexistente salvo que te lo pidan.

Test: cada linea cambiada debe trazarse a la peticion del usuario.

## 4. Goal-Driven Execution

Define criterios de exito. Itera hasta verificar.

Transforma tareas en objetivos verificables:
- "Add validation" → "Escribe tests para inputs invalidos, haz que pasen"
- "Fix the bug" → "Escribe test que reproduzca el bug, haz que pase"
- "Refactor X" → "Asegura tests verdes antes y despues"

Para tareas multi-paso, plantea plan breve:
```
1. [Paso] → verify: [check]
2. [Paso] → verify: [check]
3. [Paso] → verify: [check]
```

Criterios fuertes permiten iterar solo. Criterios debiles ("haz que funcione") requieren aclaracion constante.

---
Senal de que funciona: diffs mas limpios, menos reescrituras por sobrecomplicacion, preguntas antes de implementar.
