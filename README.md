# NestHive

> **Fusión del MVP NestLink** (gemelo digital de intralogística con AMRs — hackathon InnoLabs Nestlé fase 1) **y el proyecto AGV de ESPOL** (FlexSim + Streamlit/Néstor, traído por Andrea). Proyecto final — Fase 2, Loja.

## Estructura (ambos proyectos copiados intactos — la fusión es por adaptación, no reescritura)

### `nestlink/` — gemelo digital + flota AMR
- Backend **FastAPI** (sim a 5 Hz, seed 42, WebSocket, asignación húngara, chatbot de intents prefijados + reporte horario)
- Frontend **Next.js** (dashboard 2D, chat "💬 Asistente de flota", capa Wi-Fi con toggle)
- Demo offline + deck/one-pager en `tasksR/`
- **Arranque:** `cd nestlink && docker compose up -d --build` → web `:3000` · api `:8000`

### `agv-espol/` — lado AGV (ESPOL / Andrea)
- App **Streamlit** con panel **Néstor** (preguntas prefijadas), conector **WMS mock**
- Simulación **FlexSim** (`.fsm`) con **puente TCP** — simulación de AGVs
- **17 suites de tests** + `CALCULO_FLOTA.md` · `RENTABILIDAD_AGV.md` · `RESULTADOS_215_PT.md`
- **Arranque:** `pip install -r agv-espol/requirements.txt && streamlit run agv-espol/interfaz.py`

## Mapa de fusión (próximos pasos)

| Pieza ESPOL | Encaje en NestHive | Estado |
|---|---|---|
| `flexsim/` + `tcp_bridge` | lado AGV del gemelo (capa WCS, AGVs de cinta) | 🔜 |
| `app/services` → conector WMS | capa read-only hacia EWM/WMS | 🔜 |
| Panel **Néstor** (preguntas prefijadas) | fusionar con chatbot de intents de nestlink | 🔜 |
| `tests/` (17 suites) | correr junto a los 89 tests de nestlink | 🔜 |
| `RENTABILIDAD_AGV.md` / `CALCULO_FLOTA.md` | insumo del bloque ROI (UTPL) | 🔜 |

## Reglas del repo
- 🔒 El repo original (`mare1225.github.io/NestLink`) **sigue congelado** — este repo (NestHive) es el de desarrollo de la fase 2.
- Backend SIEMPRE en **Docker Desktop** (no OrbStack).
- Sin credenciales ni `.env` en el repo.
