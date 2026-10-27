# app/api.py
# Router FastAPI con endpoints REST, Multi-Planta y WebSocket

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Query
from app.models import (
    AdjustMissionsRequest,
    LowBatteryRequest,
    RefillRequest,
    PlantLayout,
    BlockRequest,
    UnblockRequest,
    PeakRequest,
    PlantSelectRequest,
    PlantsResponse,
    SimulationSnapshot,
    KPIsState,
    Tarea
)
from app.data_maps import PLANT_CONFIGS, load_layout_raw
from app.sim.env import sim_env
from typing import List, Dict, Any, Optional
from app.chatbot import asks as chatbot_asks, answer as chatbot_answer

router = APIRouter()

@router.get("/api/v1/chat/asks")
def get_chat_asks() -> List[Dict[str, Any]]:
    return chatbot_asks()

@router.get("/api/v1/chat/ask")
def get_chat_answer(q: str = Query(..., min_length=1)) -> Dict[str, Any]:
    return chatbot_answer(q, sim_env)

@router.get("/api/v1/chat/report")
def get_chat_report() -> Dict[str, Any]:
    return sim_env.last_hourly_report or {"event": "hourly_report_ready", "status": "pending", "sim_hour": 0}

@router.post("/api/v1/emergency/pickup")
def emergency_pickup(line: str = Query("R2", min_length=1)) -> Dict[str, Any]:
    return sim_env.trigger_emergency_pickup(line)

@router.get("/health")
def get_health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "sim_running": sim_env.is_running,
        "plant": sim_env.plant_id,
        "sim_time": sim_env.sim_time,
        "tick_id": sim_env.tick_id
    }

@router.get("/api/v1/plants", response_model=PlantsResponse)
def get_plants():
    plant_list = []
    for pid, pdata in PLANT_CONFIGS.items():
        plant_list.append({
            "id": pid,
            "nombre": pdata["nombre"],
            "layout_url": f"/api/v1/layout?plant={pid}"
        })
    return {"plants": plant_list}

@router.get("/api/v1/layout")
def get_layout(plant: Optional[str] = Query(None)) -> Dict[str, Any]:
    return load_layout_raw(plant if plant else sim_env.plant_id)

@router.post("/api/v1/sim/select")
def select_plant(payload: PlantSelectRequest):
    success = sim_env.select_plant(payload.plant)
    if not success:
        raise HTTPException(status_code=404, detail=f"Planta {payload.plant} no encontrada")
    return {"status": "ok", "plant": payload.plant}

@router.get("/api/v1/fleet")
def get_fleet() -> List[Dict[str, Any]]:
    return [amr.get_state().model_dump() for amr in sim_env.amrs]

@router.get("/api/v1/missions")
def get_missions() -> List[Dict[str, Any]]:
    return [m.model_dump() for m in sim_env.mission_queue.get_all_missions()]

@router.get("/api/v1/metrics")
def get_metrics() -> KPIsState:
    return sim_env.metrics.get_snapshot()

@router.post("/api/v1/obstacles/block")
def post_block_obstacle(payload: BlockRequest):
    success = sim_env.block_path(payload.from_node, payload.to_node, payload.tipo)
    return {
        "status": "blocked",
        "edge": [payload.from_node, payload.to_node],
        "tipo": payload.tipo,
        "success": success
    }

@router.post("/api/v1/obstacles/unblock")
def post_unblock_obstacle(payload: UnblockRequest):
    success = sim_env.unblock_path(payload.from_node, payload.to_node)
    return {
        "status": "unblocked",
        "edge": [payload.from_node, payload.to_node],
        "success": success
    }

@router.post("/api/v1/sim/peak")
def post_inject_peak(payload: PeakRequest):
    success = sim_env.inject_peak_demand(payload.line_id, payload.drain_pct)
    if not success:
        raise HTTPException(status_code=404, detail=f"Línea {payload.line_id} no encontrada")
    return {
        "status": "peak_injected",
        "line_id": payload.line_id,
        "drain_pct": payload.drain_pct
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await sim_env.bridge.connect(websocket)
    try:
        await websocket.send_json(sim_env.get_snapshot().model_dump())
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        sim_env.bridge.disconnect(websocket)
    except Exception:
        sim_env.bridge.disconnect(websocket)

@router.post("/api/v1/sim/low_battery")
def post_sim_low_battery(payload: LowBatteryRequest):
    target = sim_env.trigger_low_battery(payload.amr_id)
    if not target:
        raise HTTPException(status_code=404, detail=f"AMR {payload.amr_id} no encontrado")
    return {
        "status": "ok",
        "amr_id": payload.amr_id,
        "target": target
    }

@router.post("/api/v1/sim/refill")
def post_sim_refill(payload: RefillRequest):
    affected = sim_env.trigger_refill(payload.line_id, payload.target_pct)
    if payload.line_id is not None and payload.line_id not in affected:
        raise HTTPException(status_code=404, detail=f"Línea empacadora {payload.line_id} no encontrada")
    return {
        "status": "refill_scheduled",
        "target_pct": payload.target_pct,
        "line_id": payload.line_id,
        "lines": affected,
    }

@router.post("/api/v1/sim/reset_missions")
def post_sim_reset_missions():
    return sim_env.reset_missions()

@router.post("/api/v1/sim/adjust_missions")
def post_sim_adjust_missions(payload: AdjustMissionsRequest):
    return sim_env.adjust_missions(payload.delta)
