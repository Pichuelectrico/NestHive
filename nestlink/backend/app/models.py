# app/models.py
# Modelos Pydantic canónicos para NestLink según docs/API_CONTRATO.md

from typing import List, Tuple, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.data_maps import DEFAULT_PLANT_ID

# --- Enumeraciones del Contrato ---
EstadoAMR = Literal[
    "IDLE",
    "MOVING_TO_PICKUP",
    "LOADING",
    "MOVING_TO_DELIVERY",
    "UNLOADING",
    "WAITING_OBSTACLE",
    "REROUTING",
    "CHARGING",
    "WAITING",
    "ERROR"
]

TipoAMR = Literal["pallet_lifter", "towing_tug", "unit_load"]

TipoObstaculo = Literal["OPERATOR", "SPILL", "BLOCK"]

TipoTarea = Literal["SUPPLY_REQUEST", "PICKUP_PT", "RECHARGE", "RELOCATION", "EXPEDITION", "EXPORT"]

EstadoTarea = Literal["pendiente", "asignada", "en_curso", "completada"]

TipoNodo = Literal["linea", "empacadora", "almacen", "cruce", "carga", "buffer"]

# --- Entidades de Estado en Tiempo Real (Snapshot WS) ---

class NoticeItem(BaseModel):
    tipo: str # "PEAK", "INCIDENT", "INFO"
    line_id: Optional[str] = None
    mensaje: str
    sim_time: float

class AMRState(BaseModel):
    id: str
    nombre: str
    estado: EstadoAMR
    x: float
    y: float
    angulo: float = 0.0
    bateria: int = 100
    tarea_asignada: Optional[str] = None
    path: List[str] = []
    tipo: TipoAMR = "pallet_lifter"
    cediendo_paso: bool = False

class LineaState(BaseModel):
    id: str
    nombre: str
    material: str
    nivel_pct: float
    minutos_restantes: float
    is_packing: bool = False

class ObstaculoState(BaseModel):
    id: str
    tipo: TipoObstaculo
    x: float
    y: float
    radius: float = 2.5
    edge: Optional[List[str]] = None

class KPIsState(BaseModel):
    viajes_completados: int = 0
    viajes_vacios_evitados: int = 0
    paradas_evitadas: int = 0
    tiempo_medio_entrega_min: float = 0.0
    km_evitados: float = 0.0
    roi_km_pct: float = 0.0
    tiempo_medio_en_out_min: float = 0.0

class SimulationSnapshot(BaseModel):
    sim_time: float
    tick_id: int
    plant: str = DEFAULT_PLANT_ID
    amrs: List[AMRState]
    lines: List[LineaState]
    obstacles: List[ObstaculoState]
    kpis: KPIsState
    notices: List[NoticeItem] = [] # Retrocompatible
    # OUTs con paquete terminado esperando la entrega exclusiva al muro (id nodo → cantidad)
    out_stock: Dict[str, int] = {}

# --- Entidades del Layout de Planta ---

class NodoLayout(BaseModel):
    id: str
    x: float
    y: float
    type: TipoNodo
    label: str

class AristaLayout(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    length: float
    max_speed: float = 1.5
    direction: Literal["bi", "uni"] = "bi"
    blocked: bool = False

    model_config = ConfigDict(populate_by_name=True)

class PeatonLayout(BaseModel):
    id: str
    name: Optional[str] = None
    waypoints: List[str]
    speed: float = 1.0
    radius: float = 2.5

class CanvasLayout(BaseModel):
    w: int = 800
    h: int = 500
    title: str = "Planta Nestlé"

class PlantLayout(BaseModel):
    canvas: CanvasLayout
    nodes: List[NodoLayout]
    edges: List[AristaLayout]
    pedestrians: List[PeatonLayout] = []

# --- Entidades de Tareas y Solicitudes REST ---

class Tarea(BaseModel):
    id: str
    tipo: TipoTarea
    origen: str
    destino: str
    prioridad: int = 5
    peso_kg: float = 100.0
    estado: EstadoTarea = "pendiente"
    amr_asignado: Optional[str] = None
    created_at_sim: float = 0.0

class BlockRequest(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    tipo: TipoObstaculo = "SPILL"

    model_config = ConfigDict(populate_by_name=True)

class UnblockRequest(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")

    model_config = ConfigDict(populate_by_name=True)

class PeakRequest(BaseModel):
    line_id: str
    drain_pct: float = 30.0

class PlantSelectRequest(BaseModel):
    plant: str

class PlantItem(BaseModel):
    id: str
    nombre: str
    layout_url: str

class PlantsResponse(BaseModel):
    plants: List[PlantItem]

class LowBatteryRequest(BaseModel):
    amr_id: str

class RefillRequest(BaseModel):
    line_id: Optional[str] = None
    target_pct: float = 80.0

class AdjustMissionsRequest(BaseModel):
    delta: int = 5
