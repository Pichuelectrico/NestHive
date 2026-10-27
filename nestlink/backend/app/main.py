# app/main.py
# Entrada principal de FastAPI con ciclo de vida (Lifespan) y CORS

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.sim.env import sim_env

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Arrancar tarea en segundo plano del Tick Engine (5 Hz)
    sim_task = asyncio.create_task(sim_env.run_loop())
    print("🚀 [NestHive Backend] Motor de simulación intralogística iniciado a 5 Hz.")
    yield
    # Shutdown: Detener simulación limpiamente
    sim_env.stop()
    sim_task.cancel()
    print("🛑 [NestHive Backend] Motor de simulación detenido.")

app = FastAPI(
    title="NestHive Intralogistics API",
    description="Backend orquestador intralogístico para flota de AMRs Nestlé",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS para permitir conexiones desde Next.js (puerto 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Ruta raíz informativa: evita el confuso {"detail":"Not Found"} al abrir el backend en navegador
@app.get("/", include_in_schema=False)
async def root():
    return {
        "api": "NestHive Intralogistics API",
        "version": "1.0.0",
        "estado": "OK · simulador corriendo a 5 Hz",
        "endpoints": {
            "GET /health": "Estado y tick del simulador",
            "GET /api/v1/layout": "Mapa 2D (nodos, aristas, peatones)",
            "GET /api/v1/fleet": "Flota de AMRs",
            "GET /api/v1/missions": "Cola de misiones / kanban",
            "GET /api/v1/metrics": "KPIs y ROI",
            "POST /api/v1/obstacles/block": "Bloquear pasillo (body: from,to)",
            "POST /api/v1/obstacles/unblock": "Desbloquear pasillo (body: from,to)",
            "POST /api/v1/sim/peak": "Pico de demanda (body: line_id, drain_pct)",
            "WS /ws": "Snapshots en vivo a 5 Hz",
        },
        "frontend": "Abrir http://localhost:3000 (Next.js)",
    }
