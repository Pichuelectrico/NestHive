# 🗺️ FUSION MAP · NestHive — nestlink/ × agv-espol/

> Lead: Aion CLI · 27-oct · Contexto: **fase 2 = entrega final, demo mañana**. Regla: copiar/adaptar, no reescribir. Prioridad = impacto en la DEMO de mañana.

## 1 · Inventario funcional

### nestlink/ (gemelo digital AMR — FastAPI 5 Hz + Next.js)
| Pieza | Qué hace | Dependencias |
|---|---|---|
| `backend/app/sim`, `simulation` | Motor de simulación a 5 Hz, seed 42, WebSocket | stdlib+FastAPI |
| `backend/app/assignment` | Asignación **húngara** (urgencia·distancia·afinidad) | motor |
| `backend/app/queue`, `routing` | Cola priorizada + rutas (allow zones, AMR_06 exclusivo) | motor |
| `backend/app/api.py` | ~17 endpoints REST (estado, layout, estrategia, flota) | FastAPI |
| `backend/app/chatbot.py` + `env.py` | **Chatbot de intents** (`/chat/asks`, `/chat/ask`) + **reporte horario** (WS `hourly_report_ready`, `/chat/report`) — ✅ verificado en vivo | estado del motor |
| `backend/app/iot`, `metrics.py` | Telemetría Wi-Fi/edge + KPIs | motor |
| `frontend/components/{Dashboard,PlantMap,ControlPanel,FleetChatPanel}.tsx` | Dashboard 2D, mapa con capa Wi-Fi (toggle), panel 💬 con reporte horario | lib/api.ts |
| `frontend/lib/DemoEngine` (offline) | Demo sin backend (plan B) | — |
| `tests/` | **89 tests** (API + rounds) | pytest |
| `tasksR/` | Deck 13 slides, guion, one-pager, Q&A, runbook | — |

### agv-espol/ (lado AGV — Streamlit + FlexSim, ESPOL/Andrea)
| Pieza | Qué hace | Dependencias |
|---|---|---|
| `app/models/` (agv, bateria, mision, pallet, solicitud) | Modelo de dominio AGV | — |
| `app/services/simulador_flota.py`, `gestor_flota.py` | Simulador/gestor de flota AGV propia | models |
| `app/services/nestor.py`, `preguntas_nestor.py` | **Panel Néstor**: preguntas prefijadas + respuestas | services |
| `app/services/conector_wms.py` + `wms_mock.py` | **Conector WMS (mock)** — envío idempotente de movimientos de pallet por HTTP y consulta de salud/listado | — |
| `app/services/indicadores_capacidad.py` | Indicadores de capacidad (equivalente a nuestro techo/Sakasegawa) | — |
| `app/services/{bateria_flota,alertas_linea,inventario_transito,escenarios,analizador_operativo,estado_visual,exportacion_nestor}.py` | Batería, alertas de línea, inventario en tránsito, escenarios, análisis | services |
| `flexsim/` (`.fsm` + `tcp_bridge`) | **Simulación FlexSim de AGVs con puente TCP** | FlexSim (propietario) |
| `tests/` | **15 módulos / 171 funciones de prueba** (la ejecución completa requiere las dependencias de `requirements.txt`) | pytest |
| `CALCULO_FLOTA.md`, `RENTABILIDAD_AGV.md`, `RESULTADOS_215_PT.md` | Cálculo de flota y rentabilidad (215 PT ✓ coincide con nuestras 215 salidas/turno) | — |

## 2 · Mapa de fusión

| # | Fusión | Cómo | Esfuerzo | Impacto demo | Prioridad |
|---|---|---|---|---|---|
| F1 | **Néstor ↔ chatbot de intents** | Extraer preguntas de `preguntas_nestor.py` que aporten (inventario en tránsito, alertas de línea) → añadir como intents en `chatbot.py` | **S** (2-3 h) | Medio | 🔴 hoy |
| F2 | **conector_wms ↔ capa EWM read-only** | Adaptar `wms_mock.py` como fuente alternativa de órdenes → endpoint `GET /api/v1/wms/orders` (read-only) en `api.py`; el panel puede mostrar "órdenes WMS recibidas" | **S-M** (3-4 h) | **Alto** (evidencia visible de "integración") | 🔴 hoy si hay tiempo |
| F3 | **flexsim/tcp_bridge ↔ adaptador WCS (AGVs)** | Opción A (riesgosa): backend acepta "AGVs" externos vía TCP. **Opción B (recomendada):** AGV = "AMR restringido" en el motor propio (allowed_types + zonas) — el puente FlexSim queda como referencia documentada | M-L | Alto pero **no para mañana** | 🟡 día 2 |
| F4 | **tests ESPOL + nestlink** | Ejecutar los 15 módulos ESPOL junto a los 89 de NestLink; publicar la cifra solo después de instalar dependencias y obtener un resultado verde (171 funciones descubiertas localmente). | **S** (30 min) | Medio (credibilidad) | 🔴 hoy |
| F5 | **RENTABILIDAD/CALCULO_FLOTA ↔ bloque ROI** | Cruzar números con el informe (215 PT ✓); detectar discrepancias antes del jurado | **S** (1 h) | Medio | 🟡 |

## 3 · Orden de ejecución recomendado (hoy)

1. **F4** (30 min, riesgo cero) → cifra combinada de tests.
2. **F1** (2-3 h) → el chatbot hereda las mejores preguntas de Néstor.
3. **F2** (si quedan ≥3 h) → endpoint WMS read-only visible en demo.
4. **F3-OpB / F5** → día 2 o solo mención en el pitch.

## 4 · Top-5 riesgos de integración

1. **Doble fuente de verdad de KPIs** (motor propio vs simulador de ESPOL) — decidir UNA fuente para la demo (la nuestra, ya verificada).
2. **FlexSim es propietario** — no corre en Docker; su puente TCP no es demostrable en el venue → solo mención documentada.
3. **Tiempo**: demo mañana; cualquier cambio al motor (F3) puede romper los 89 tests → congelar motor, solo añadir endpoints.
4. **Dos stacks** (Streamlit vs FastAPI+Next) — no intentar UIs unificadas antes del evento.
5. **Branding**: "Néstor" (ESPOL) vs "Asistente de flota" (NestHive) — unificar nombre en la demo (NestHive).

## 5 · Nota de gobernanza

- Repo público de desarrollo (push permitido). Repo original NestLink **congelado**.
- Todo cambio de código que toque el motor requiere pase del lead + 89 tests en verde.
