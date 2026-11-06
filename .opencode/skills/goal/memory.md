---
updated: 2026-11-03
version: 4
limit: 2200
limit_user: 1375
mode: hard
---

# Goal — Memoria usuario (curada, límite duro estilo Hermes)
# Reglas: 2.200 chars; un add que exceda exige batch remove/patch+add. Ver memory/README.md

## Preferencias (max 35)
- [2026-11-05] respuestas: 60 palabras / 5 líneas, resumen llano primero, datos interpretados; `detalla`→15 líneas
- [2026-10-21] si la tarea externa no depende del agente (web/build/deploy), goal-wait sin devolver turno

## Hechos (max 35)
- [2026-11-02] Goal: proof en research/<exp>/traces/<hash>.r1/.r2.proof; lab/ prohibido
- [2026-11-03] LightGBM2: .mqh = motor viejo bit a bit (4/4); .ex5 delta=0; libreria == motor
- [2026-11-03] GPU MQL5: kernel exacto = hash identico; fp32 local+bins63 = 3,10x a 150k x30 y 0,25x a 20k (cruce ~100k)
- [2026-11-03] LightGBM2: pesos a 1 = hash identico; metricas = sklearn 9 dec; PredictRaw NO suma initv
- [2026-11-03] LightGBM2: L1/huber/quantile arrancan en la media (si no, q0.9 cubre 43%); GOSS/DART neutros = hash igual
- [2026-11-03] LightGBM2 paridad: bins=FindBinWithZeroAsOneBin, corte cnt=round(hess*n/sumh); SetParity+BuildLightGBM 150/150 delta 6e-12
- [2026-11-03] Bateria 1:1: 5 casos, 4/4 perdidas +-0,01, rank 1,0; IR v2 recarga delta 0
- [2026-11-03] PyTorch.mqh: 8/8 delta<=4,44e-16; OpenCL bloqueado por CLSetKernelArg(buffer)

- [2026-11-04] PyTorch.mqh: 19/19 (BatchNorm, pools, GRU, MHA, NLL/Huber/KLDiv, RMSprop/Adagrad); falta multicapa/bidir

- [2026-11-04] PyTorch.mqh: 22/22 (pila LSTM, bidir, Transformer post-norm); Transformer deriva a 2 pasos

- [2026-11-04] PyTorch.mqh: 22/22 a 1e-12; 2 pasos ya 1:1 (LayerNorm: gamma dentro de las sumas)

- [2026-11-04] PyTorch.mqh: 23/23; Adam/AdamW 1:1 con betas no estandar (meta entrecomillado)

- [2026-11-04] ALGLIB vs PyTorch.mqh: 2,1x mas rapido en 4-5-3, empate en 20-64-64-1; MLPSetNeuronInfo revienta

- [2026-11-04] PyTorch.mqh GPU ON: CLSetKernelArgMem (no CLSetKernelArg); 6,7x a 4,2M y 34x a 33,6M; umbral PT_GPU_MIN_MAC=1e6

- [2026-11-04] PyTorch.mqh: refuerzo 29/29 (discreto+Normal); PPO 1:1 a 3,33e-16; 2 llamadas RNG en args MQL = orden incierto
- [2026-11-06] LightGBM Real RNG = LCG 214013*x+2531011 (no mt19937); bagging Bernoulli por fila, seed bagging_seed+bloque 65536, sin resiembra por iter

## Anti-patrones (max 20)
- [2026-10-17] no usar Jev ni Console fuera de GO
- [2026-10-17] no auto-inyectar memoria completa en CONTEXT.md

## Pendientes (max 10)
- [2026-11-03] /goal = flujo completo por defecto; `--fast` solo explicito; /goal-full retirado
- [2026-11-02] Goal: no le falta inteligencia, le falta parar y anotar (11/15 sin leccion); cierre opt-in
- [2026-11-02] compactar memoria cada ~5 goals (sin hook automatico)
- [2026-11-02] MQL5 iATR/iMA/iRSI devuelven HANDLE: leer con CopyBuffer; exportar sl_pct para verificar
