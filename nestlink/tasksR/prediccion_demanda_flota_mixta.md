# [Fase 2 · Investigación] Predicción de demanda (software-only) + flota mixta 2 AMR + N AGVs

> **Nota del lead:** entregado por Aion CLI (takeover) tras dos ciclos sin entrega de Cursor (interrupt aceptado, turn sin output). Misma regla: solo documento, sin código, 🔒 sin git. Números SOLO del banco canónico; supuestos marcados ⚠️.

## 1. Predicción de demanda con los datos que YA genera el sim

**Premisa clave:** la simulación ya produce la serie temporal que un predictor necesita — cada PICKUP_PT consume insumo de su línea cada `LINE_PROCESS_TIME_SEC = 20 s`, cada SUPPLY_REQUEST llega con prioridad P8-P10, y todo queda en el estado que el backend difunde por WebSocket. **No hay que instrumentar nada nuevo: hay que leer lo que ya existe** (ring buffer de eventos de consumo por línea/SKU en `app/sim/env.py`).

### Qué predice en la práctica
- **Horizonte:** "la línea E1 estará vacía en ~23 min (sim)" → crear **SUPPLY_REQUEST anticipado** ANTES de que el gauge cruce el umbral de 25 %.
- **Efecto en el orquestador:** la misión entra a la cola P1–P10 con **prioridad calculada por urgencia prevista**, no reactiva. El húngaro la asigna con más holgura → menos esperas en línea, menos picos de flota.

### Métodos por complejidad creciente (elige el mínimo que funcione)

| Método | Qué necesita | Qué captura | Esfuerzo | Veredicto |
|---|---|---|---|---|
| **Media móvil** (últimos N consumos) | ring buffer | ritmo base | 0,5 día | piso mínimo |
| **Suavizado exponencial** (α ajustable) | idem + 1 parámetro | ritmo base + tendencia reciente | 0,5 día | ✅ **recomendado para demo** |
| **Estacionalidad por turno** (perfil horario por SKU/turno) | históricos por turno | picos predecibles del turno | 1 día | fase 2 viva |
| Regresión simple (consumo ~ carga de línea) | features extra | correlaciones | 1–2 días | sobre-ingeniería para el demo |

⚠️ Todos son **estimaciones de esfuerzo dev** sobre el código existente; ninguno requiere ML real ni dependencias nuevas.

### Regla anti-pico (obligatoria)
El backend ya tiene `POST /api/v1/sim/peak` (pico de demanda). El predictor **debe degradarse con gracia** ante cambio de régimen: si la tasa real se desvía >X % de la prevista durante M muestras, descarta el forecast y vuelve a modo reactivo (comportamiento actual). **La predicción es un extra, nunca un riesgo para la demo.**

## 2. Valor en rúbrica

- **Propuesta de Valor (20 %):** el pitch pasa de *"responde rápido"* (reactivo) a **"prevé y abastece antes de que la línea lo pida"** (preventivo). Es LA frase diferenciadora frente a un orquestador convencional.
- **Factibilidad (20 %):** 100 % software sobre datos propios del sim → sin hardware, sin dependencias nuevas.
- **Escalabilidad (15 %):** el predictor es agnóstico de planta: funciona con los 3 mapas (quito, guayaquil, realistic).
- **ODS 9:** industria más eficiente con menos desperdicio de material (menos stock-outs → menos reproceso).

## 3. Demo feasibility (sin romper nada)

- **Frontend:** cada gauge de línea gana un chip predictivo: **"⏱ vacío en ~23 min"** + badge **"JIT predictivo"** cuando el forecast está activo (gris = predictivo desactivado). Cambio cosmético en el componente de gauges; `npm run dev` + tsc validan.
- **Backend:** módulo `sim/predictor.py` (forecast por línea) + campo `predicted_empty_min` en el snapshot WS. La cola muestra las misiones anticipadas con etiqueta **"anticipada"** — se VE al orquestador adelantarse.
- **Momento de demo:** activar el pico (`sim/peak`) → los gauges predictivos se adelantan y la flota reacciona ANTES. Efecto "wow" sin tocar el flujo canónico.
- **Esfuerzo total:** ≈1–1,5 día-dev (predictor 0,5–1 + frontend 0,5). **NO implementar antes de Loja sin decidir el equipo**; el doc de investigación basta para el pitch.

> **Herencia fase 1:** el plan original de FlowPilot ya contemplaba un "módulo predictivo JIT (gauge de minutos restantes por línea)" como opcional, y en [[01 Proyecto/Ideas Descartadas]] quedó registrado que el **JIT Loop ganó con 9.5** (orquestación just-in-time reactiva). La predicción de demanda es el **paso natural siguiente del mismo concepto**: mismo espíritu, ahora preventivo. No contradice ninguna decisión: la regla de descarte era "sin hardware" — y esto es 100 % software.

## 4. Flota mixta: ¿escala el motor a 2 AMR + N AGVs?

**Respuesta corta: SÍ — el motor ya está diseñado para ser agnóstico del vehículo; lo que hay que añadir es restricción de movimiento y coste por tipo.**

### 4.1 Los 3 cambios (todos acotados)

| Cambio | Dónde | Qué es | Esfuerzo ⚠️ |
|---|---|---|---|
| **Grafo por tipos** | `data_maps.py` (`build_plant_graph`) | atributo `allowed_types` por arista: `"amr"` (libre) vs `"agv"` (solo-cinta). A* ya acepta filtro de aristas → rutas AGV = subgrafo de cinta | 0,5–1 día |
| **Matriz de coste por tipo** | módulo de asignación (húngaro) | para cada (vehículo, misión): coste = A* en SU subgrafo; **∞ si infactible** (AGV fuera de su cinta). El húngaro no cambia: solo su matriz de entrada | 0,5 día |
| **Zonas-mutex en cruces** | `env.py` (obstáculos/bloqueos) | en cada cruce AMR-vs-AGV, celda de exclusión mutua con **preferencia al AGV** (no puede esquivar); el AMR cede con su lógica de evasión existente | 1 día |

**Truco de demo muy potente:** en la simulación, **un AGV = AMR restringido** (clase con velocidad menor ~0,5–1,0 m/s, sin evasión dinámica, rutas solo por su subgrafo de cinta). Así el MVP puede **demostrar la flota híbrida 100 % en software** — mismo dashboard, mapa pinta la cinta, AMRs verdes esquivan, AGVs naranjas circulan su carril. Sin hardware, sin WCS real (la capa WCS/adaptador PLC es de implementación real, no del demo; ver [[tasksR/investigacion_agv_hibrido_fase2.md | doc AGV]] §3).

### 4.2 Lo que NO cambia
- Cola P1–P10, prioridades, contrato VDA 5050 con EWM (los AGVs son opacos para SAP: el WCS traduce), KPIs, batería/cargadores.
- El **piloto canónico (2 AMR, $0,22M, reversible <1 turno) sigue exactamente igual** — la flota mixta es una **opción de escalado posterior**, no un requisito del piloto.

## 5. Riesgo de techo con solo 2 AMR (la matemática)

**2 AMR solos NO cubren un turno completo.** Con la equivalencia canónica (techo 411 con 5 unidades de línea → ≈82 pallets/turno por AMR-equivalente ⚠️ lineal):

| Configuración | Unidades de línea (equivalentes) | Techo ≈ pallets/turno | ¿Cubre demanda 215 (pico 301)? |
|---|---|---|---|
| **2 AMR solos** (1 línea + 1 reserva) | 1,0 | **≈82** | ❌ ni de cerca |
| 2 AMR + 4 AGV (eficacia 0,70–0,85 ⚠️) | 3,8–4,4 | ≈312–361 | ✅ justo |
| 2 AMR + 5 AGV | 4,5–5,25 | ≈370–430 | ✅ como el base |
| Base 6 AMR (5+1) | 5,0 | 411 (+91 %) | ✅ con margen |

La cuenta del requisito: 2,13 pallets/min → ×1,4 pico → ÷0,75 (regla ≤75 % de Sakasegawa) = **≈3,98 AMR-equivalentes**. Los 2 AMR aportan 1 (el otro es reserva N+1); **los AGVs aportan el resto**. Por eso la respuesta correcta al jurado no es "sí, 2 AMRs bastan", sino:

> **"2 AMRs + la mezcla correcta de AGVs en rutas fijas cubren el turno — y NestHive decide la mezcla con datos, no con fe"** (validable en la simulación antes de comprar nada).

**Condición innegociable:** la reserva N+1 es SIEMPRE AMR (único que rescata una cinta bloqueada) y la eficacia AGV/AMR (0,70–0,85 ⚠️) se mide en el piloto con 1 AGV de prueba en la ruta rosada antes de fijar la mezcla final.

## 6. Listo para la slide

**5 bullets:**
1. **De reactivo a preventivo:** NestHive predice cuándo cada línea pedirá insumo y crea la misión ANTES — el gauge muestra "vacío en ~23 min" y la flota se adelanta.
2. **100 % software:** el predictor lee el historial que el sistema ya genera (suavizado exponencial, sin ML, sin hardware nuevo).
3. **Flota mixta soportada por diseño:** grafo con aristas "solo-cinta" + húngaro con coste ∞ fuera de ruta: AMR flexible, AGV barato en rutas fijas, un solo cerebro.
4. **La mezcla se calcula, no se adivina:** takt 132 s → ≈4 vehículos-equivalentes; 2 AMR + 4–5 AGV cubren el turno con CAPEX −24 % y payback ≈3,8 años (estimación a validar en piloto).
5. **Seguridad ante todo:** la reserva N+1 siempre es AMR y el forecast se degrada solo ante cambios de régimen — la predicción nunca arriesga la operación.

**3 preguntas probables del jurado:**

- **"¿Y si la predicción se equivoca?"**
  La operación no depende de ella: si el forecast se desvía de la tasa real, se descarta solo y el sistema vuelve a su modo reactivo actual (el que ya demostramos). La predicción adelanta misiones; jamás cancela ni bloquea. Peor caso = comportamiento de hoy.

- **"¿Por qué no ML/neuronas para predecir?"**
  Porque con los datos de un turno, un suavizado exponencial bien calibrado ya anticipa el stock-out con la precisión que la operación necesita — y es explicable ante cualquier auditor. Metemos complejidad solo cuando los datos la justifiquen, no para el slide.

- **"¿Un AGV atascado no bloquea toda la línea?"**
  Por eso el diseño es híbrido y no todo-AGV: la reserva N+1 es AMR y puede tomar la misión de cualquier cinta bloqueada — el húngaro la reasigna en el siguiente tick. Además, la simulación nos deja probar esta falla ANTES de que exista en la planta.

---

### Supuestos a validar
- Horizonte de forecast útil (se asume 20–40 min sim ⚠️) y α del suavizado — calibrar con seed 42 reproducible.
- Eficacia AGV/AMR 0,70–0,85 y coste de cinta — ver doc AGV, se miden en el piloto.
- Que el equipo humano decide implementar el predictor + flota mixta en el MVP después de Loja (hoy es propuesta).
