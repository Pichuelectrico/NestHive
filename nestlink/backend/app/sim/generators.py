# app/sim/generators.py
# Simulación IoT de consumo, producción continua y restock para todas las líneas de marca

from typing import List, Dict, Any, Optional
from app.models import LineaState
from app.sim.assignment import MissionQueue

BRAND_MP_MAP = {
    "nescafé": "WH_MP_3",
    "nescafe": "WH_MP_3",
    "l1": "WH_MP_3",
    "maggi": "WH_MP_4",
    "l2": "WH_MP_4",
    "nestum": "WH_MP_5",
    "l3": "WH_MP_5",
    "savoy": "WH_MP_1",
    "e1": "WH_MP_1",
    "lechera": "WH_MP_2",
    "e2": "WH_MP_2",
}

BRAND_PT_MAP = {
    "nescafé": "WH_PT_1",
    "nescafe": "WH_PT_1",
    "l1": "WH_PT_1",
    "maggi": "WH_PT_2",
    "l2": "WH_PT_2",
    "nestum": "WH_PT_3",
    "l3": "WH_PT_3",
    "savoy": "WH_PT_1",
    "e1": "WH_PT_1",
    "lechera": "WH_PT_2",
    "e2": "WH_PT_2",
}

def resolve_mp_origin(line_id: str, line_nombre: str) -> str:
    """Mapeo inequívoco de marca a su almacén de materias primas e insumos correspondiente."""
    name_low = line_nombre.lower()
    id_low = line_id.lower()
    for k, v in BRAND_MP_MAP.items():
        if k in name_low or k == id_low:
            return v
    return "WH_MP_1"

def resolve_pt_destination(line_id: str, line_nombre: str) -> str:
    """Mapeo de marca a su almacén de producto terminado correspondiente."""
    name_low = line_nombre.lower()
    id_low = line_id.lower()
    for k, v in BRAND_PT_MAP.items():
        if k in name_low or k == id_low:
            return v
    return "WH_PT_1"

class ProductionLine:
    # Ronda 13: tiempo de proceso de la línea (~20 s) antes de emitir el PICKUP_PT a Paletizado
    LINE_PROCESS_TIME_SEC: float = 20.0
    # Un insumo entregado repone RESTOCK_PCT y alcanza para PALLETS_PER_SUPPLY generaciones
    # de pallets: el desgaste ocurre por pallet generado, no de forma continua.
    RESTOCK_PCT: float = 20.0
    PALLETS_PER_SUPPLY: int = 3
    PALLET_DRAIN_PCT: float = RESTOCK_PCT / PALLETS_PER_SUPPLY

    def __init__(self, id_str: str, nombre: str, material: str, tasa_kg_min: float, umbral_critico_pct: float, nivel_inicial_pct: float):
        self.id = id_str
        self.nombre = nombre
        self.material = material
        self.tasa_kg_min = tasa_kg_min
        self.umbral_critico_pct = umbral_critico_pct
        self.nivel_pct = nivel_inicial_pct
        # Ronda 5.1: Todas las líneas de marca consumen insumos y producen PT
        self.is_packing = True
        self.refill_target_pct = 80.0
        self.factor_drenaje = 1.1
        self.peak_multiplier = 1.0
        self.peak_duration_sec = 0.0
        # Ronda 13: acumulador determinista de tiempo de proceso del lote actual
        self.processing_secs: float = 0.0

    def inject_peak(self, multiplier: float = 3.0, duration_sec: float = 300.0, drain_pct: float = 30.0):
        self.peak_multiplier = multiplier
        self.peak_duration_sec = duration_sec
        self.nivel_pct = max(4.0, self.nivel_pct - drain_pct)

    def restock(self, amount_pct: float = 20.0):
        """Aumenta el nivel de insumos al completarse una entrega SUPPLY_REQUEST."""
        self.nivel_pct = min(100.0, self.nivel_pct + amount_pct)

    def drain_pickup(self, amount_pct: Optional[float] = None):
        """Desgaste de insumo por pallet generado (retirado en PICKUP_PT): 1/3 de un restock."""
        amount = (self.PALLET_DRAIN_PCT if amount_pct is None else amount_pct) * self.peak_multiplier
        self.nivel_pct = max(0.0, self.nivel_pct - amount)

    def step(self, dt_sim: float, mission_queue: MissionQueue, sim_time: float, metrics_manager: Any):
        if self.peak_duration_sec > 0:
            self.peak_duration_sec -= dt_sim
            if self.peak_duration_sec <= 0:
                self.peak_multiplier = 1.0

        # El consumo ya no es continuo: se descuenta por pallet generado (ver drain_pickup).

        # Ronda 13: Línea → Paletizado (~20 s de proceso). Mientras haya insumo, se acumula
        # tiempo de proceso y, al cumplirse los 20 s, se encadena una misión PICKUP_PT
        # (Línea → WH_PT de la marca) para que un AMR lleve el PT a Paletizado.
        if self.nivel_pct > 0.0:
            self.processing_secs += dt_sim
            if self.processing_secs >= self.LINE_PROCESS_TIME_SEC:
                self.processing_secs = 0.0
                if self.nivel_pct >= 15.0:
                    pending_pt = [
                        m for m in mission_queue.get_all_missions()
                        if m.tipo == "PICKUP_PT"
                        and m.origen == self.id
                        and m.estado in ["pendiente", "asignada", "en_curso"]
                    ]
                    if not pending_pt:
                        pt_dest = resolve_pt_destination(self.id, self.nombre)
                        mission_queue.add_mission(
                            tipo="PICKUP_PT",
                            origen=self.id,
                            destino=pt_dest,
                            prioridad=7,
                            peso_kg=480.0,
                            sim_time=sim_time
                        )

        # Refill dirigido: encadena SUPPLY_REQUEST hasta alcanzar el objetivo de insumos (≥80%)
        if self.nivel_pct < self.refill_target_pct:
            pending_or_active = [
                m for m in mission_queue.get_all_missions()
                if m.destino == self.id and m.estado in ["pendiente", "asignada", "en_curso"]
            ]
            if not pending_or_active:
                wh_origin = resolve_mp_origin(self.id, self.nombre)
                prio = 10 if self.nivel_pct <= self.umbral_critico_pct else 8
                mission_queue.add_mission(
                    tipo="SUPPLY_REQUEST",
                    origen=wh_origin,
                    destino=self.id,
                    prioridad=prio,
                    peso_kg=180.0,
                    sim_time=sim_time
                )
                if self.nivel_pct <= self.umbral_critico_pct:
                    metrics_manager.record_stoppage_prevented()

    def get_state(self) -> LineaState:
        rate = max(self.tasa_kg_min * self.peak_multiplier, 0.1)
        mins = round((self.nivel_pct / rate) * 1.5, 1)
        return LineaState(
            id=self.id,
            nombre=self.nombre,
            material=self.material,
            nivel_pct=round(self.nivel_pct, 1),
            minutos_restantes=mins,
            is_packing=self.is_packing
        )

class PlantDemandGenerator:
    def __init__(self, seeds_data: Dict[str, Any]):
        self.fleet_rules = seeds_data.get("fleet_rules", {})
        self.espol_flow = self.fleet_rules.get("flow") == "espol_supply_to_palet"
        self._supply_due = {f"INSUMO_P{i}": 0.0 for i in range(1, 4)} if self.espol_flow else {}
        self._pickup_due: List[tuple[float, int]] = []
        self.reco_stock = {f"RECO_R{i}": 0 for i in range(1, 4)} if self.espol_flow else {}
        self._palet_index = 0
        self._next_reco_sim = 110.0
        self._reco_index = 0
        self.lines: List[ProductionLine] = []
        for line in seeds_data.get("lines", []):
            self.lines.append(
                ProductionLine(
                    id_str=line["id"],
                    nombre=line["nombre"],
                    material=line["material"],
                    tasa_kg_min=float(line.get("tasa_consumo_kg_min", 4.0)),
                    umbral_critico_pct=float(line.get("umbral_critico_pct", 30.0)),
                    nivel_inicial_pct=float(line.get("nivel_inicial_pct", 50.0))
                )
            )

    def restock_line(self, line_id: str, amount_pct: float = 20.0) -> bool:
        for line in self.lines:
            if line.id == line_id:
                line.restock(amount_pct)
                return True
        return False

    def supply_delivered(self, destination: str, sim_time: float) -> None:
        """La cinta lleva la producción de Pn a Rn; ningún vehículo circula por ella."""
        if not self.espol_flow or destination not in self._supply_due:
            return
        station = int(destination[-1])
        self.restock_line(f"R{station}", amount_pct=ProductionLine.RESTOCK_PCT)
        process = float(self.fleet_rules.get("process_seconds", 20.0))
        for n in range(1, ProductionLine.PALLETS_PER_SUPPLY + 1):
            self._pickup_due.append((sim_time + process * n, station))
        self._supply_due[destination] = sim_time + float(self.fleet_rules.get("supply_interval_seconds", 110.0))

    def espol_supply_destination(self, line_id: str) -> str:
        recovery = self.fleet_rules.get("pickup_node", {}).get(line_id, "RECO_R1")
        return f"INSUMO_P{recovery[-1]}"

    def drain_line_pickup(self, line_id: str, amount_pct: Optional[float] = None) -> bool:
        """Cada pallet retirado consume 1/3 de un insumo entregado (amount_pct se ignora)."""
        if self.espol_flow and line_id.startswith("RECO_R"):
            self.reco_stock[line_id] = max(0, self.reco_stock.get(line_id, 0) - 1)
            line_id = f"R{line_id[-1]}"
        amount_pct = None
        for line in self.lines:
            if line.id == line_id:
                line.drain_pickup(amount_pct)
                return True
        return False

    def set_refill_target(self, line_id: Optional[str], target_pct: float) -> List[str]:
        """Fija el objetivo de insumos (default 80%) de una o todas las líneas."""
        affected: List[str] = []
        tgt = max(40.0, min(100.0, target_pct))
        for line in self.lines:
            if line_id is not None and line.id != line_id:
                continue
            line.refill_target_pct = tgt
            affected.append(line.id)
        return affected

    def force_supply(self, line_id: str, mission_queue: MissionQueue, sim_time: float, force: bool = False) -> bool:
        """Encola un SUPPLY_REQUEST desde el almacén de MP correspondiente de la marca."""
        for line in self.lines:
            if line.id != line_id:
                continue
            if self.espol_flow:
                destination = self.espol_supply_destination(line_id)
                if any(m.tipo == "SUPPLY_REQUEST" and m.destino == destination
                       and m.estado in ("pendiente", "asignada", "en_curso")
                       for m in mission_queue.get_all_missions()):
                    return False
                mission_queue.add_mission("SUPPLY_REQUEST", "FUENTE_INSUMOS", destination,
                                          prioridad=10 if force else 8, peso_kg=180.0,
                                          sim_time=sim_time, force_urgent=force)
                self._supply_due[destination] = float("inf")
                return True
            if not force and line.nivel_pct >= line.refill_target_pct:
                return False
            pending_or_active = [
                m for m in mission_queue.get_all_missions()
                if m.destino == line.id and m.estado in ["pendiente", "asignada", "en_curso"]
            ]
            if pending_or_active:
                return False
            wh_origin = resolve_mp_origin(line.id, line.nombre)
            prio = 10 if line.nivel_pct <= line.umbral_critico_pct else 8
            mission_queue.add_mission(
                tipo="SUPPLY_REQUEST",
                origen=wh_origin,
                destino=line.id,
                prioridad=prio,
                peso_kg=180.0,
                sim_time=sim_time,
                force_urgent=force
            )
            return True
        return False

    def step(self, dt_sim: float, mission_queue: MissionQueue, sim_time: float, metrics_manager: Any):
        if self.espol_flow:
            for line in self.lines:
                if line.peak_duration_sec > 0:
                    line.peak_duration_sec = max(0.0, line.peak_duration_sec - dt_sim)
                    if line.peak_duration_sec == 0:
                        line.peak_multiplier = 1.0
            active = ("pendiente", "asignada", "en_curso")
            for destination, due in self._supply_due.items():
                if sim_time >= due and not any(m.tipo == "SUPPLY_REQUEST" and m.destino == destination
                                               and m.estado in active for m in mission_queue.get_all_missions()):
                    mission_queue.add_mission("SUPPLY_REQUEST", "FUENTE_INSUMOS", destination,
                                              prioridad=8, peso_kg=180.0, sim_time=sim_time)
                    self._supply_due[destination] = float("inf")
            waiting = []
            for due, station in self._pickup_due:
                if sim_time < due:
                    waiting.append((due, station))
                    continue
                origin = f"RECO_R{station}"
                self.reco_stock[origin] += 1
            self._pickup_due = waiting
            for origin, count in self.reco_stock.items():
                if count <= 0 or any(m.tipo == "PICKUP_PT" and m.origen == origin and m.estado in active
                                     for m in mission_queue.get_all_missions()):
                    continue
                destination = f"PALET_{self._palet_index % 15 + 1:02d}"
                self._palet_index += 1
                mission_queue.add_mission("PICKUP_PT", origin, destination, prioridad=8,
                                          peso_kg=480.0, sim_time=sim_time)
            return
        for line in self.lines:
            line.step(dt_sim, mission_queue, sim_time, metrics_manager)
        if self.fleet_rules.get("enabled") and sim_time >= self._next_reco_sim:
            origins = ("RECO_R1", "RECO_R2", "RECO_R3")
            origin = origins[self._reco_index % len(origins)]
            if not any(m.origen == origin and m.estado in ("pendiente", "asignada", "en_curso")
                       for m in mission_queue.get_all_missions()):
                destination = f"PALET_{(self._reco_index % 15) + 1:02d}"
                mission_queue.add_mission("PICKUP_PT", origin, destination, prioridad=8,
                                          peso_kg=480.0, sim_time=sim_time)
                self._reco_index += 1
            self._next_reco_sim += 110.0

    def inject_peak(self, line_id: str, drain_pct: float = 30.0, mission_queue: MissionQueue = None, sim_time: float = 0.0) -> bool:
        for line in self.lines:
            if line.id == line_id:
                line.inject_peak(multiplier=3.0, duration_sec=300.0, drain_pct=drain_pct)
                if mission_queue:
                    if self.espol_flow:
                        self.force_supply(line_id, mission_queue, sim_time, force=True)
                        return True
                    wh_origin = resolve_mp_origin(line.id, line.nombre)
                    mission_queue.add_mission(
                        tipo="SUPPLY_REQUEST",
                        origen=wh_origin,
                        destino=line.id,
                        prioridad=10,
                        peso_kg=220.0,
                        sim_time=sim_time,
                        force_urgent=True
                    )
                return True
        return False

    def get_snapshot(self) -> List[LineaState]:
        return [line.get_state() for line in self.lines]
