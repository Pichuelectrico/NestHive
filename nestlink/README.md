# NestLink — Cerebro Orquestador Intralogístico (Reto 1 · Hackathon InnoLabs Nestlé)

> **Tagline:** *El Waze + cerebro de Nestlé para que sus AMRs nunca vayan vacíos y sus líneas nunca paren.*
> **Evento:** 4 sept · 8:30–18:30 · Salón Azul USFQ · Premio USD 1.000 · Equipo 2 devs (React + Python)
> **Demo:** 100% software con datos simulados · Tick engine 5 Hz · WebSocket en vivo

NestLink orquesta una flota de 5 AMRs sobre el grafo de la planta: cola priorizada + asignación húngara + rutas A* con reruteo dinámico ante bloqueos y peatones. Todo visible en un dashboard en vivo (mapa 2D + kanban + gauges + ROI).

## Novedades y Capacidades del MVP (Ronda 5 Final)

- ⚡ **Rellenado Estratégico Dirigido por Objetivo (`POST /api/v1/sim/refill`):** Botón *«Rellenar 80% / TODAS»* que encadena misiones `SUPPLY_REQUEST` con **+20% por viaje** (~4 viajes por línea) hasta $\ge 80\%$.
- ⟳ **Gestión de cola en vivo (R5.2):** Botón *«Reiniciar tareas»* (`POST /api/v1/sim/reset_missions`) y botones *«＋5 / −5 misiones»* (`POST /api/v1/sim/adjust_missions {delta: ±5}`) para mostrar la cola reactiva en demo.
- 🔋 **Gestión Energética Realista y Autocarga Orgánica:** Consumo continuo de batería proporcional al tiempo en movimiento. Autocarga automática al alcanzar $\le 15\%$ o forzada mediante botón demo *«🔋 15% Batería»* (`POST /api/v1/sim/low_battery`), con **selección de cargador occupancy-aware** (reparte la flota entre `CHARGER_1`/`CHARGER_2` por ocupación + distancia real, sin amontonar todos en el mismo cargador) y validación de estado `CHARGING`.
- 🏭 **Soporte Multi-Planta en Caliente:** Conmutación dinámica entre Planta Quito (22 nodos, 5 AMRs) y CD Guayaquil (27 nodos, 6 AMRs) mediante `GET /api/v1/plants` y `POST /api/v1/sim/select` sin pérdida de conexión WebSocket.
- 🚦 **Ruteo Dinámico $A^*$ y Desvíos Inteligentes:** Bloqueo de aristas con derrames simulados (`POST /api/v1/obstacles/block`) y detección de operarios peatones con frenado de seguridad preventivo.
- 🎯 **Algoritmo Húngaro con Afinidad de Zona (*Home-Zone*):** Despacho óptimo de flota asignando AMRs a sus líneas naturales para máxima coherencia visual y $\ge 4$ robots activos simultáneamente.
- 🧪 **Suite Completa de 27 Tests Automatizados (100% Verdes):** Cobertura total de modelos, grafos, endpoints REST, WebSocket, FSM de AMRs, recarga, restock y multi-planta.
- 🐳 **Docker Compose Integral (`compose.yml`):** Orquestación lista para producción con servicios `api` y `web`, healthchecks automáticos y build arguments para entorno Next.js.

## Stack

| Capa | Tec |
|------|-----|
| Frontend | Next.js 14 (App Router) + Tailwind + Recharts + Framer Motion |
| Backend | Python 3.11 + FastAPI + Uvicorn · networkx (A*) · scipy (húngaro) · websockets |
| Tiempo real | WebSocket `/ws` snapshots 5 Hz + LERP 60 fps en front · Fallback offline (`demoEngine`) |
| Datos | `plant_layout.json` (22 nodos, 30 aristas, 2 peatones) + `seed.json` (4 líneas, 5 AMRs) |

## Estructura real

```
Hackathon_InnoLabs_MVP_Plan/
├── README.md
├── PLAN_COMPLETO_NestLink.md        # plan integral del MVP
├── PLAN_COMPLETO_MVP.md / NestLink_Reto1.md / 02_NestScan_VisionTwin_Reto2.md
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py                  # FastAPI + lifespan (tick engine)
│   │   ├── api.py                   # REST /api/v1/* + WS /ws
│   │   ├── models.py                # Pydantic (Snapshot, AMR, Tarea, etc.)
│   │   ├── data_maps.py             # carga layout → DiGraph
│   │   ├── metrics.py               # KPIs
│   │   ├── app/data/maps/plant_layout.json
│   │   ├── app/data/seeds/seed.json
│   │   └── sim/
│   │       ├── env.py               # loop 5 Hz
│   │       ├── routing.py           # A* (networkx)
│   │       ├── assignment.py        # húngaro (scipy)
│   │       ├── agents.py            # FSM AMR
│   │       ├── generators.py        # consumo líneas → misiones
│   │       ├── obstacles.py         # peatones + bloqueos
│   │       └── bridge.py            # ConnectionManager WS
│   └── tests/
│       ├── test_smoke.py
│       └── test_api_integration.py
├── frontend/
│   ├── app/ (layout.tsx, page.tsx, globals.css)
│   ├── components/ (PlantMap, KanbanPanel, LineGauges, KpiBar, ControlPanel, Dashboard, Header, TrendsPanel)
│   ├── hooks/ (useSimulation, useLayout)
│   ├── lib/ (api.ts, types.ts, config.ts, demoEngine.ts, amrColors.ts)
│   ├── public/maps/plant_layout.json  # copia para render del mapa
│   ├── next.config.mjs / tailwind.config.ts / tsconfig.json / package.json
│   └── .next/ (build)
├── prototype/
│   └── index.html                   # prototipo HTML previo
└── docs/
    ├── API_CONTRATO.md              # contrato Front↔Back (snapshot + endpoints)
    ├── 03_Simulacion_Intralogistica_NestLink.md
    ├── GUIA_EJECUCION_Y_DEMO.md
    ├── MEJORAS_PROPUESTAS.md
    └── MEJORAS_UI_ROUTING.md        # emojis de carga/batería + animación de rutas
```

## Cómo levantar (local)

**Backend** (http://localhost:8000):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# docs: http://localhost:8000/docs
```

**Frontend** (http://localhost:3000):
```bash
cd frontend
npm install
# opcional: NEXT_PUBLIC_API_URL=http://localhost:8000  (por defecto ese)
npm run dev
```

> Ambos deben correr a la vez. El front conecta por WS a `NEXT_PUBLIC_API_URL/ws`. Si el back no está, el front entra en **modo offline** (demoEngine con datos pre-grabados, sin perder la demo).

## Endpoints clave

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | `/health` | healthcheck + tick |
| GET | `/api/v1/layout` | layout canónico |
| GET | `/api/v1/fleet` · `/api/v1/missions` · `/api/v1/metrics` | flota, misiones, KPIs |
| POST | `/api/v1/obstacles/block` `{"from","to","tipo"}` | bloquea arista y rerutea |
| POST | `/api/v1/obstacles/unblock` `{"from","to"}` | desbloquea |
| POST | `/api/v1/sim/peak` `{"line_id","drain_pct"}` | inyecta pico de demanda |
| WS | `/ws` | snapshots 5 Hz (`sim_time, tick_id, amrs, lines, obstacles, kpis`) |

## Docker (alternativa con un comando)

Cuando `compose.yml` esté disponible (lo crea Antigravity):
```bash
docker compose up --build
# front en http://localhost:3000, back en http://localhost:8000
```
`NEXT_PUBLIC_API_URL` se inyecta como build ARG del frontend; ver `.env.example`.

## Variables de entorno

Copiar `.env.example` → `.env.local` (no commitear). Variables clave: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`, `PUERTO_BACK/FRONT`. `SIM_SPEED_FACTOR` y `SIM_SEED` están hardcodeados en `backend/app/sim/env.py` (4.0 / 42); si el backend los expone por env, documentarlos en `.env.example`.

Contrato completo en `docs/API_CONTRATO.md`. Guía de demo en `docs/GUIA_EJECUCION_Y_DEMO.md`.
