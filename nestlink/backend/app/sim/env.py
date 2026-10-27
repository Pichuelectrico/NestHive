# app/sim/env.py
# Bucle maestro de simulación (Tick Engine 5 Hz) con soporte Multi-Planta

import asyncio
import math
import random
from typing import List, Dict, Any, Optional
from app.models import SimulationSnapshot, NoticeItem
from app.data_maps import load_layout_raw, load_seeds_raw, build_plant_graph, PLANT_CONFIGS, TEST_PLANTS, DEFAULT_PLANT_ID, get_plant_config
from app.metrics import KPIManager
from app.sim.routing import block_edge, unblock_edge, find_shortest_path
from app.sim.assignment import MissionQueue, compute_hungarian_assignment
from app.sim.obstacles import ObstacleManager
from app.sim.generators import PlantDemandGenerator
from app.sim.agents import AMRAgent
from app.sim.amr_yield import AmrYieldResolver
from app.sim.bridge import ConnectionManager
from app.chatbot import hourly_report

class SimulationEnvironment:
    FREEZE_TIMEOUT_S: float = 90.0

    def __init__(self, plant_id: str = DEFAULT_PLANT_ID):
        self.plant_id = plant_id
        self.SIM_SPEED_FACTOR: float = 4.0
        self.TICK_INTERVAL_SEC: float = 0.2  # 5 Hz
        self.is_running: bool = False
        self.sim_time: float = 0.0
        self.tick_id: int = 0
        self.notices: List[NoticeItem] = []
        self.last_hourly_report: Optional[Dict[str, Any]] = None
        self._last_report_sim_hour: int = 0

        self.edge_reservations: set[tuple[str, str, float]] = set()
        self.bridge = ConnectionManager()
        self.init_plant(plant_id)

    def reserve_path(self, amr: AMRAgent, path: List[str], horizon_sec: float = 15.0):
        if not path or len(path) < 2:
            return
        expiry = self.sim_time + horizon_sec
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            self.edge_reservations.add((u, v, expiry))

    def release_reservations(self, tick_time: float):
        self.edge_reservations = {(u, v, exp) for (u, v, exp) in self.edge_reservations if exp > tick_time}

    def init_plant(self, plant_id: str):
        random.seed(42)
        self.plant_id = plant_id
        self.layout_raw = load_layout_raw(plant_id)
        self.seeds_raw = load_seeds_raw(plant_id)
        self.G, self.node_positions = build_plant_graph(self.layout_raw)
        
        # Mapeo de tipos de nodo {id: type} (linea, empacadora, almacen, cruce, carga)
        self.node_types = {n["id"]: n.get("type", "cruce") for n in self.layout_raw.get("nodes", [])}

        # Nodos de expedición (OUT*) → buffer de producto terminado; nodo de entrega al muro externo
        self.out_nodes: List[str] = sorted(nid for nid in self.node_positions if nid.startswith("OUT"))
        self.wall_node: Optional[str] = next((nid for nid in self.node_positions
                                              if nid in ("MURO_ENTREGA", "ENTREGA_MURO", "WALL_DOCK")), None)
        self.out_stock: Dict[str, int] = {out: 0 for out in self.out_nodes}
        # Control de asignaciones OUT: nº de misiones EXPORT provisionadas (en ruta/al muro) por OUT.
        # Estado/sincronización: out_stock = paquetes EN el buffer (🟡 emoji 📦);
        # out_en_ruta = EXPORTs ya PROGRAMADAS (máx 1 extra sobre stock, encadena en out_ship).
        self.out_en_ruta: Dict[str, int] = {out: 0 for out in self.out_nodes}
        # KPI "tiempo en OUT": cola FIFO de instantes de arribo de paquetes por OUT (para medir
        # cuánto espera cada paquete en el buffer antes de la entrega exclusiva al muro).
        self._out_pkg_arrivals: Dict[str, List[float]] = {out: [] for out in self.out_nodes}
        self.delivery_amr_id: Optional[str] = None

        self.metrics = KPIManager()
        self.last_hourly_report = None
        self._last_report_sim_hour = 0
        self.mission_queue = MissionQueue()
        self.obstacle_manager = ObstacleManager(self.layout_raw, self.node_positions)
        self.generator = PlantDemandGenerator(self.seeds_raw)

        # Flota de AMRs con Home-Zone y node_types
        self.amrs: List[AMRAgent] = []
        home_zones_map = {
            "AMR_01": "L1_OUT",
            "AMR_02": "E1_IN",
            "AMR_03": "L2_OUT",
            "AMR_04": "E2_IN",
            "AMR_05": "L3_OUT" if "L3_OUT" in self.node_positions else None,
            "AMR_06": None
        }

        for amr_data in self.seeds_raw.get("amrs", []):
            aid = amr_data["id"]
            if amr_data.get("entrega_exclusiva") or amr_data.get("tipo") == "delivery" or (self.wall_node and aid == "AMR_06"):
                self.delivery_amr_id = aid
            hz = amr_data.get("home_zone", home_zones_map.get(aid))
            if not hz and aid == self.delivery_amr_id:
                hz = self.wall_node
            self.amrs.append(
                AMRAgent(
                    id_str=aid,
                    nombre=amr_data["nombre"],
                    tipo=amr_data.get("tipo", "pallet_lifter"),
                    velocidad_ms=float(amr_data.get("velocidad_ms", 1.5)),
                    carga_kg=float(amr_data.get("carga_kg", 500.0)),
                    bateria_inicial=int(amr_data.get("bateria_inicial", 100)),
                    posicion_nodo=amr_data.get("posicion_nodo", "CHARGER_1"),
                    home_zone=hz,
                    node_positions=self.node_positions,
                    node_types=self.node_types,
                    charger_resolver=lambda aid: self.find_best_charger(aid)
                )
            )

        # Misiones iniciales para activación inmediata con orígenes por marca
        self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_1", "E1_IN", prioridad=10, sim_time=0.0)
        self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_3", "L1_OUT", prioridad=8, sim_time=0.0)
        self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_2", "E2_IN", prioridad=10, sim_time=0.0)
        self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_4", "L2_OUT", prioridad=8, sim_time=0.0)

    def select_plant(self, plant_id: str) -> bool:
        if plant_id not in PLANT_CONFIGS and plant_id not in TEST_PLANTS:
            return False
        self.init_plant(plant_id)
        self.add_notice("INFO", None, f"Simulación reiniciada con {get_plant_config(plant_id)['nombre']}")
        return True

    def add_notice(self, tipo: str, line_id: Optional[str], mensaje: str):
        self.notices.append(NoticeItem(tipo=tipo, line_id=line_id, mensaje=mensaje, sim_time=self.sim_time))
        if len(self.notices) > 5:
            self.notices.pop(0)

    async def run_loop(self):
        self.is_running = True
        while self.is_running:
            start_t = asyncio.get_event_loop().time()
            dt_sim = self.TICK_INTERVAL_SEC * self.SIM_SPEED_FACTOR
            self.sim_time += dt_sim
            self.tick_id += 1

            # Limpiar avisos tras 15s simulados
            self.notices = [n for n in self.notices if (self.sim_time - n.sim_time) < 15.0]

            # 0. Liberar reservas caducadas
            self.release_reservations(self.sim_time)

            # 1. Demanda IoT y consumo continuo
            self.generator.step(dt_sim, self.mission_queue, self.sim_time, self.metrics)

            # 1b. Autocarga orgánica: si la batería cae ≤15%, el AMR prioriza ir al cargador más cercano
            self._auto_recharge_check()

            # 2. Reubicación preventiva para AMRs ociosos (umbral reducido a 2.0s para flujo continuo)
            for amr in self.amrs:
                if amr.estado == "IDLE" and amr.idle_timer > 2.0 and amr.id != self.delivery_amr_id:
                    is_on_operational_node = self.node_types.get(amr.posicion_nodo) in ["linea", "empacadora", "almacen"]
                    target_hub = amr.home_zone if (amr.home_zone and self.node_types.get(amr.home_zone) not in ["linea", "empacadora", "almacen"]) else ("X_02" if "X_02" in self.node_positions else list(self.node_positions.keys())[0])
                    if amr.posicion_nodo != target_hub or is_on_operational_node:
                        self.mission_queue.add_mission("RELOCATION", amr.posicion_nodo, target_hub, prioridad=2, sim_time=self.sim_time)
                        amr.idle_timer = 0.0

            # 3. Entrega exclusiva al muro (EXPORT): solo el AMR designado, solo si hay stock en OUT
            self._dispatch_exports()

            # 3b. Asignación Húngara con validación de ruta (EXPORT fuera del pool; AMR exclusivo reservado)
            idle_amrs = [a for a in self.amrs if a.estado == "IDLE" and a.id != self.delivery_amr_id]
            pending_missions = [m for m in self.mission_queue.get_pending_missions() if m.tipo != "EXPORT"]
            if idle_amrs and pending_missions:
                assignments = compute_hungarian_assignment(idle_amrs, pending_missions, self.node_positions)
                for amr, mission in assignments:
                    success = amr.assign_mission(mission, self.G, env=self)
                    if not success:
                        # Si no pudo rutear, la misión permanece pendiente y el AMR sigue libre
                        mission.estado = "pendiente"
                        mission.amr_asignado = None

            # 4. Peatones
            self.obstacle_manager.step(dt_sim)
            active_obstacles = self.obstacle_manager.get_snapshot()

            # 4b. Evasión y resolución de conflictos AMR<->AMR (cabeceo)
            AmrYieldResolver.resolve_amr_conflicts(self, dt_sim)

            # 5. Cinemática de AMRs (con callback a generator para restock y drain)
            for amr in self.amrs:
                amr.step(dt_sim, self.G, active_obstacles, self.metrics, self.sim_time, self.generator, env=self)

            self.check_freeze_timeouts()

            # 6. Broadcast WS
            snapshot = self.get_snapshot()
            await self.bridge.broadcast_snapshot(snapshot.model_dump())
            # Reporte horario con reloj simulado (4x: cada 900 s reales aprox.).
            sim_hour = int(self.sim_time // 3600)
            if sim_hour > self._last_report_sim_hour:
                self.last_hourly_report = hourly_report(self, self.last_hourly_report)
                self._last_report_sim_hour = sim_hour
                await self.bridge.broadcast_snapshot(self.last_hourly_report)

            # 7. Sleep a 5 Hz
            elapsed = asyncio.get_event_loop().time() - start_t
            sleep_time = max(0.01, self.TICK_INTERVAL_SEC - elapsed)
            await asyncio.sleep(sleep_time)

    def _amr_blocked_by_pedestrian(self, amr: AMRAgent, obstacles: List[Any]) -> bool:
        """Mismo criterio PEM que agents.step: peatón OPERATOR dentro del radio de seguridad."""
        for obs in obstacles:
            if obs.tipo != "OPERATOR":
                continue
            dx = (obs.x - amr.x) / 10.0
            dy = (obs.y - amr.y) / 10.0
            if math.sqrt(dx * dx + dy * dy) < obs.radius:
                return True
        return False

    def _is_pedestrian_stationary(self, amr: AMRAgent, min_seconds: float = 15.0) -> bool:
        """Comprueba si el peatón cerca del AMR ha estado estacionario (sin cambiar posición) por >= min_seconds."""
        active_obstacles = self.obstacle_manager.get_snapshot()
        for obs in active_obstacles:
            if obs.tipo != "OPERATOR":
                continue
            dx = (obs.x - amr.x) / 10.0
            dy = (obs.y - amr.y) / 10.0
            if math.sqrt(dx * dx + dy * dy) < obs.radius:
                # Encontrar el PedestrianAgent en obstacle_manager
                for ped in self.obstacle_manager.pedestrians:
                    if ped.id == obs.id:
                        # Si sólo tiene 1 waypoint o no tiene waypoints
                        if not ped.waypoints or len(ped.waypoints) <= 1:
                            return True
                        # Trackear última posición conocida del peatón
                        last_pos = getattr(ped, "_last_pos", (ped.x, ped.y))
                        last_t = getattr(ped, "_last_pos_time", self.sim_time)
                        dist_moved = math.hypot(ped.x - last_pos[0], ped.y - last_pos[1])
                        if dist_moved > 1.0:
                            ped._last_pos = (ped.x, ped.y)
                            ped._last_pos_time = self.sim_time
                        elif (self.sim_time - last_t) >= min_seconds:
                            return True
        return False

    def check_freeze_timeouts(self):
        """Si un AMR permanece atascado >= FREEZE_TIMEOUT_S sim, forzar descongelamiento determinista.

        Descongelación para REROUTING, WAITING_OBSTACLE y WAITING.
        Si hay un peatón cerca, solo se espera indefinidamente si el peatón está en movimiento.
        Si el peatón es estacionario (inmóvil por >15s), se ignora temporalmente para no bloquear forever.
        """
        active_obstacles = self.obstacle_manager.get_snapshot()
        sorted_amrs = sorted(self.amrs, key=lambda a: a.id)
        for amr in sorted_amrs:
            if amr.estado not in ["REROUTING", "WAITING_OBSTACLE", "WAITING"]:
                continue
            if amr.estado == "WAITING_OBSTACLE" and self._amr_blocked_by_pedestrian(amr, active_obstacles):
                # Si el peatón está en movimiento, es una espera legítima
                if not self._is_pedestrian_stationary(amr, min_seconds=15.0):
                    continue

            duracion = self.sim_time - getattr(amr, "_estado_desde", self.sim_time)
            if duracion < self.FREEZE_TIMEOUT_S:
                continue

            prev_estado = amr.estado
            dest = amr.tarea_actual.destino if (amr.tarea_actual and amr.tarea_actual.estado == "en_curso") else (amr.tarea_actual.origen if amr.tarea_actual else None)
            new_path = None
            if dest:
                new_path = find_shortest_path(self.G, amr.posicion_nodo, dest, self.node_positions)

            if new_path:
                amr.path = new_path
                amr.target_node_idx = 1 if len(new_path) > 1 else 0
                amr.cediendo_paso = False
                if len(new_path) <= 1:
                    amr.estado = "UNLOADING" if (amr.tarea_actual and amr.tarea_actual.estado == "en_curso") else "LOADING"
                else:
                    amr.estado = "MOVING_TO_DELIVERY" if (amr.tarea_actual and amr.tarea_actual.estado == "en_curso") else "MOVING_TO_PICKUP"
                amr._estado_desde = self.sim_time
                self.add_notice("INFO", None, f"Descongelando tras {int(self.FREEZE_TIMEOUT_S)}s en {prev_estado}: {amr.nombre} retoma ruta")
            else:
                if amr.tarea_actual:
                    amr.tarea_actual.estado = "pendiente"
                    amr.tarea_actual.amr_asignado = None
                    amr.tarea_actual = None
                amr.estado = "IDLE"
                amr.path = []
                amr.cediendo_paso = False
                amr._estado_desde = self.sim_time
                self.add_notice("INFO", None, f"Descongelando: {amr.nombre} vuelve a IDLE sin ruta")

    def step_tick(self, dt_sim: Optional[float] = None):
        """Ejecuta un tick síncrono completo de simulación (útil para tests y stepping)."""
        if dt_sim is None:
            dt_sim = self.TICK_INTERVAL_SEC * self.SIM_SPEED_FACTOR
        self.sim_time += dt_sim
        self.tick_id += 1

        self.release_reservations(self.sim_time)
        self.notices = [n for n in self.notices if (self.sim_time - n.sim_time) < 15.0]
        self.generator.step(dt_sim, self.mission_queue, self.sim_time, self.metrics)
        self._auto_recharge_check()

        for amr in self.amrs:
            if amr.estado == "IDLE" and amr.idle_timer > 2.0 and amr.id != self.delivery_amr_id:
                is_on_operational_node = self.node_types.get(amr.posicion_nodo) in ["linea", "empacadora", "almacen"]
                target_hub = amr.home_zone if (amr.home_zone and self.node_types.get(amr.home_zone) not in ["linea", "empacadora", "almacen"]) else ("X_02" if "X_02" in self.node_positions else list(self.node_positions.keys())[0])
                if amr.posicion_nodo != target_hub or is_on_operational_node:
                    self.mission_queue.add_mission("RELOCATION", amr.posicion_nodo, target_hub, prioridad=2, sim_time=self.sim_time)
                    amr.idle_timer = 0.0

        # Entrega exclusiva al muro (EXPORT): solo el AMR designado, solo si hay stock en OUT
        self._dispatch_exports()

        idle_amrs = [a for a in self.amrs if a.estado == "IDLE" and a.id != self.delivery_amr_id]
        pending_missions = [m for m in self.mission_queue.get_pending_missions() if m.tipo != "EXPORT"]
        if idle_amrs and pending_missions:
            assignments = compute_hungarian_assignment(idle_amrs, pending_missions, self.node_positions)
            for amr, mission in assignments:
                success = amr.assign_mission(mission, self.G, env=self)
                if not success:
                    mission.estado = "pendiente"
                    mission.amr_asignado = None

        self.obstacle_manager.step(dt_sim)
        active_obstacles = self.obstacle_manager.get_snapshot()

        # Evasión AMR<->AMR
        AmrYieldResolver.resolve_amr_conflicts(self, dt_sim)

        for amr in self.amrs:
            amr.step(dt_sim, self.G, active_obstacles, self.metrics, self.sim_time, self.generator, env=self)

        self.check_freeze_timeouts()

    def stop(self):
        self.is_running = False

    def block_path(self, u: str, v: str, tipo: str = "SPILL") -> bool:
        block_edge(self.G, u, v)
        self.obstacle_manager.add_block(u, v, tipo)
        self.add_notice("INCIDENT", None, f"Derrame reportado en tramo {u} ↔ {v}")
        return True

    def unblock_path(self, u: str, v: str) -> bool:
        unblock_edge(self.G, u, v)
        self.obstacle_manager.remove_block(u, v)
        self.add_notice("INFO", None, f"Tramo {u} ↔ {v} despejado")
        return True

    def find_best_charger(self, amr_id: str) -> Optional[str]:
        """
        Selección inteligente de estación de carga (occupancy-aware):
        1. Identifica ocupación real de cada estación (AMRs cargando o con RECHARGE activo).
        2. Calcula el costo real de ruta A* ponderado por longitud de aristas.
        3. Prioriza cargadores completamente libres (costo ASC); si todos están ocupados,
           selecciona el de MENOR ocupación (desempate por menor costo de ruta).
        """
        target_amr = next((a for a in self.amrs if a.id == amr_id), None)
        if not target_amr:
            return None

        # Determinar nodo de inicio más preciso según las coordenadas (x, y) actuales del AMR
        start_node = target_amr.posicion_nodo
        if hasattr(target_amr, "x") and hasattr(target_amr, "y"):
            min_d_sq = float("inf")
            for nid, (nx, ny) in self.node_positions.items():
                d_sq = (target_amr.x - nx) ** 2 + (target_amr.y - ny) ** 2
                if d_sq < min_d_sq:
                    min_d_sq = d_sq
                    start_node = nid

        chargers = [nid for nid, ntype in self.node_types.items() if ntype == "carga"]
        if not chargers:
            return "CHARGER_1" if "CHARGER_1" in self.node_positions else None

        candidates = []
        for ch in chargers:
            path = find_shortest_path(self.G, start_node, ch, self.node_positions)
            if not path:
                continue

            cost = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                if self.G.has_edge(u, v):
                    cost += float(self.G[u][v].get("weight", self.G[u][v].get("length", 1.0)))
                else:
                    cost += 1.0

            occupancy = 0
            for other in self.amrs:
                if other.id == amr_id:
                    continue
                if other.estado == "CHARGING" and other.posicion_nodo == ch:
                    occupancy += 1
                elif other.tarea_actual and other.tarea_actual.tipo == "RECHARGE" and other.tarea_actual.destino == ch and other.tarea_actual.estado in ["asignada", "en_curso"]:
                    occupancy += 1

            for m in self.mission_queue.get_all_missions():
                if m.tipo != "RECHARGE" or m.destino != ch:
                    continue
                if m.estado not in ("pendiente", "asignada", "en_curso"):
                    continue
                if m.amr_asignado == amr_id:
                    continue
                # Evitar doble conteo si ya contado vía tarea_actual del otro AMR
                owner = next((a for a in self.amrs if a.tarea_actual and a.tarea_actual.id == m.id), None)
                if owner and owner.tarea_actual and owner.tarea_actual.destino == ch:
                    continue
                occupancy += 1

            candidates.append({
                "charger_id": ch,
                "path": path,
                "cost": cost,
                "occupancy": occupancy
            })

        if not candidates:
            return None

        # Ordenar por: 1º menor ocupación, 2º menor costo de ruta
        candidates.sort(key=lambda c: (c["occupancy"], c["cost"]))
        return candidates[0]["charger_id"]

    def trigger_low_battery(self, amr_id: str) -> Optional[str]:
        target_amr = next((a for a in self.amrs if a.id == amr_id), None)
        if not target_amr:
            return None

        target_amr.bateria = 15.0

        best_charger = self.find_best_charger(amr_id)
        if not best_charger:
            self.add_notice("WARNING", amr_id, f"Sin cargadores accesibles para {target_amr.nombre}")
            return None

        if target_amr.tarea_actual:
            # Si el AMR exclusivo interrumpe un EXPORT en vuelo (fue a recargar), NO puede
            # dejar el OUT atrapado: se revierte el estado (paquete al buffer / slot liberado)
            # y se reprograma para que la entrega sí ocurra cuando vuelva.
            if target_amr.tarea_actual.tipo == "EXPORT":
                self.abort_export(target_amr.tarea_actual)
            target_amr.tarea_actual.estado = "completada"

        recharge_mission = self.mission_queue.add_mission(
            tipo="RECHARGE",
            origen=target_amr.posicion_nodo,
            destino=best_charger,
            prioridad=8,
            peso_kg=0.0,
            sim_time=self.sim_time,
            force_urgent=True
        )

        target_amr.assign_mission(recharge_mission, self.G)
        self.add_notice("LOW_BATTERY", amr_id, f"Batería baja en {target_amr.nombre} (15%) → En ruta hacia {best_charger}")
        return best_charger

    def _auto_recharge_check(self):
        """Autocarga orgánica: si la batería cae ≤15%, el AMR interrumpe y prioriza el cargador."""
        for amr in self.amrs:
            if (
                amr.estado != "CHARGING"
                and amr.bateria <= 15.0
                and not (amr.tarea_actual and amr.tarea_actual.tipo == "RECHARGE")
            ):
                self.trigger_low_battery(amr.id)

    def _dispatch_exports(self) -> None:
        """Entrega EXCLUSIVA al muro externo (ruta rosada): solo el AMR designado (delivery_amr_id)
        ejecuta misiones EXPORT, y solo existe una si hay stock (paquete terminado) en algún OUT."""
        if not self.delivery_amr_id or not self.wall_node or not self.out_nodes:
            return
        amr = next((a for a in self.amrs if a.id == self.delivery_amr_id), None)
        if not amr or amr.estado != "IDLE":
            return
        for m in self.mission_queue.get_pending_missions():
            if m.tipo != "EXPORT":
                continue
            if amr.assign_mission(m, self.G, env=self):
                # Nota informativa; el emoji se apagará cuando el AMR recoja (LOADING en OUT)
                return
        return

    def pick_best_out(self, from_node: Optional[str] = None) -> str:
        """Elige el OUT con MENOR carga: primero menos paquetes esperando (stock), luego menos
        entrega programada (EXPORTs en ruta + pallets EN TRANSITO vía EXPEDITION ya asignadas).
        Robusto ante dos pallets encadenando EXPEDITION en el mismo tick (no los junta)."""
        if not self.out_nodes:
            return "OUT"
        def score(out: str):
            stock = self.out_stock.get(out, 0)
            planned = self.out_en_ruta.get(out, 0) + sum(
                1 for m in self.mission_queue.get_all_missions()
                if m.tipo == "EXPEDITION" and m.destino == out
                and m.estado in ["pendiente", "asignada", "en_curso"]
            )
            # dist: desempate leve (si un OUT quedara inalcanzable, penalizarlo fuerte)
            dist = 0
            if from_node and from_node != out:
                path = find_shortest_path(self.G, from_node, out, self.node_positions)
                dist = len(path) if path else 10 ** 9
            return (stock, planned, dist if dist < 10 ** 8 else 10 ** 8, out)
        return min(self.out_nodes, key=score)

    def out_arrive(self, out_id: str, sim_time: float) -> None:
        """Control de estados OUT: un paquete terminado llega al buffer (stock+1, emoji 📦).
        SOLO si aún no hay EXPORT programada para este OUT, provisiona UNA (out_en_ruta).
        Dos llegadas en el mismo instante suman 2 al stock pero NO duplican el EXPORT:
        el excedente lo encadena out_ship al entregar en el muro."""
        if out_id not in self.out_stock or not self.wall_node:
            return
        self.out_stock[out_id] += 1
        # KPI: registrar instante de arribo del paquete al buffer OUT (se cierra en out_ship)
        self._out_pkg_arrivals[out_id].append(sim_time)
        self._provision_export(out_id, sim_time=sim_time)

    def _provision_export(self, out_id: str, sim_time: Optional[float] = None) -> bool:
        """Point único de creación de misiones EXPORT: provisiona UNA EXPORT hacia el muro externo
        SOLO si hay stock esperando en el OUT y no hay otra ya programada (out_en_ruta==0).
        Devuelve True si creó una misión. Lo usan out_arrive, out_ship y abort_export."""
        if out_id not in self.out_stock or not self.wall_node or not self.delivery_amr_id:
            return False
        if self.out_en_ruta.get(out_id, 0) > 0:
            return False
        if self.out_stock[out_id] <= 0:
            return False
        st = self.sim_time if sim_time is None else sim_time
        self.mission_queue.add_mission(
            tipo="EXPORT",
            origen=out_id,
            destino=self.wall_node,
            prioridad=7,
            peso_kg=480.0,
            sim_time=st
        )
        self.out_en_ruta[out_id] += 1
        self.add_notice("INFO", None, f"📦 Paquete en {out_id} esperando recolección del AMR exclusivo (muro externo)")
        return True

    def abort_export(self, mission) -> None:
        """El AMR exclusive interrumpe un EXPORT en vuelo (p.ej. fue a recargar batería).
        Revierte el estado OUT para que ningún paquete quede atrapado para siempre:
        - Si aún no había recogido ('asignada'), el paquete sigue en el buffer → solo se libera
          el slot (en_ruta−1) y se reprograma si hay stock.
        - Si ya lo llevaba en vuelo ('en_curso'), vuelve a poner el paquete en el buffer (stock+1),
          registra de nuevo su arribo (el reloj de espera se reinicia) y reprograma la EXPORT."""
        out = getattr(mission, "origen", None)
        if out not in self.out_stock:
            return
        picked_up = getattr(mission, "estado", None) == "en_curso"
        if picked_up:
            self.out_stock[out] += 1
            self._out_pkg_arrivals[out].append(self.sim_time)
        if self.out_en_ruta.get(out, 0) > 0:
            self.out_en_ruta[out] = max(0, self.out_en_ruta[out] - 1)
        self._provision_export(out)
        self.add_notice(
            "WARNING", None,
            (f"EXPORT interrumpida: AMR exclusivo fue a recargar → paquete de {out} devuelto al buffer"
             if picked_up else f"EXPORT interrumpida: AMR exclusivo fue a recargar → {out} reprogramado")
        )

    def out_pickup(self, out_id: str, amr_name: str = "") -> None:
        """El AMR exclusivo recoge del OUT: el paquete sale del buffer (stock−1, emoji se apaga)
        y viaja al muro en vuelo. out_en_ruta NO cambia: esa misión sigue contando hasta entregar.
        El instante de arribo queda en la cola FIFO y se cierra (tiempo de espera) en out_ship."""
        if out_id not in self.out_stock:
            return
        self.out_stock[out_id] = max(0, self.out_stock[out_id] - 1)
        if amr_name:
            self.add_notice("INFO", None, f"{amr_name} recogió paquete de {out_id} → rumbo a {self.wall_node}")

    def out_ship(self, out_id: str, amr_name: str = "") -> None:
        """El AMR exclusivo entrega en el muro (pared externa): la misión EXPORT deja de contar
        (en_ruta−1). Cierra el KPI de espera del paquete (arribo→entrega). Si aún queda stock
        esperando en ese OUT, encadena la siguiente EXPORT — con contador explícito no hay guard
        falso (en curso ya no aparece como pendiente)."""
        if out_id not in self.out_stock:
            return
        self.out_en_ruta[out_id] = max(0, self.out_en_ruta.get(out_id, 0) - 1)
        # KPI: tiempo de espera del paquete en OUT = instante de entrega (ahora) − instante de arribo
        arrivals_q = self._out_pkg_arrivals.get(out_id)
        if arrivals_q:
            t0 = arrivals_q.pop(0)
            self.metrics.record_out_wait_sec(max(0.0, self.sim_time - t0))
        self.add_notice("INFO", None, f"🚚 {amr_name or 'AMR'} entregó paquete de {out_id} en {self.wall_node} (pared externa, embarque)")
        self._provision_export(out_id)

    def reset_missions(self) -> Dict[str, Any]:
        cleared_count = len(self.mission_queue.missions)
        self.mission_queue.missions = []
        self.mission_queue._counter = 1

        for amr in self.amrs:
            amr.tarea_actual = None
            amr.path = []
            if amr.estado not in ["CHARGING"]:
                amr.estado = "IDLE"

        m1 = self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_1", "E1_IN", prioridad=10, sim_time=self.sim_time)
        m2 = self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_3", "L1_OUT", prioridad=8, sim_time=self.sim_time)
        m3 = self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_2", "E2_IN", prioridad=10, sim_time=self.sim_time)
        m4 = self.mission_queue.add_mission("SUPPLY_REQUEST", "WH_MP_4", "L2_OUT", prioridad=8, sim_time=self.sim_time)

        self.add_notice("INFO", None, f"Misiones reiniciadas: {cleared_count} limpiadas, 4 activas")
        return {
            "status": "ok",
            "missions_clearadas": cleared_count,
            "activas": [m.model_dump() for m in [m1, m2, m3, m4]]
        }

    def adjust_missions(self, delta: int) -> Dict[str, Any]:
        from app.sim.generators import resolve_mp_origin
        if delta > 0:
            sorted_lines = sorted(self.generator.lines, key=lambda l: l.nivel_pct)
            added = []
            for i in range(abs(delta)):
                target_line = sorted_lines[i % len(sorted_lines)]
                wh_origin = resolve_mp_origin(target_line.id, target_line.nombre)
                m = self.mission_queue.add_mission(
                    tipo="SUPPLY_REQUEST",
                    origen=wh_origin,
                    destino=target_line.id,
                    prioridad=8,
                    peso_kg=180.0,
                    sim_time=self.sim_time,
                    force_urgent=True
                )
                added.append(m.model_dump())
            self.add_notice("INFO", None, f"+{delta} tareas encoladas")
            return {
                "status": "ok",
                "delta": delta,
                "misiones_nuevas": added,
                "pendientes": len(self.mission_queue.get_pending_missions())
            }
        elif delta < 0:
            count_to_remove = abs(delta)
            removed_count = 0
            new_list = []
            for m in self.mission_queue.missions:
                if m.estado == "pendiente" and removed_count < count_to_remove:
                    removed_count += 1
                    continue
                new_list.append(m)
            self.mission_queue.missions = new_list
            self.add_notice("INFO", None, f"-{removed_count} tareas pendientes eliminadas")
            return {
                "status": "ok",
                "delta": delta,
                "removidas": removed_count,
                "pendientes": len(self.mission_queue.get_pending_missions())
            }
        else:
            return {
                "status": "ok",
                "delta": 0,
                "pendientes": len(self.mission_queue.get_pending_missions())
            }

    def inject_peak_demand(self, line_id: str, drain_pct: float = 30.0) -> bool:
        success = self.generator.inject_peak(line_id, drain_pct=drain_pct, mission_queue=self.mission_queue, sim_time=self.sim_time)
        if success:
            self.add_notice("PEAK", line_id, f"Pico de demanda inyectado en {line_id}")
        return success

    def trigger_refill(self, line_id: Optional[str] = None, target_pct: float = 80.0) -> List[str]:
        """Fija el objetivo de insumos (≥80%) y encadena SUPPLY_REQUEST hasta alcanzarlo."""
        affected = self.generator.set_refill_target(line_id, target_pct)
        if not affected:
            return []
        # Encola de inmediato una entrega por cada línea afectada bajo su objetivo
        for lid in affected:
            self.generator.force_supply(lid, self.mission_queue, self.sim_time, force=True)
        label = line_id if line_id else "todas las empacadoras"
        self.add_notice("INFO", line_id, f"Relleno activado: objetivo {target_pct:.0f}% de insumos en {label}")
        return affected

    def get_snapshot(self) -> SimulationSnapshot:
        return SimulationSnapshot(
            sim_time=round(self.sim_time, 1),
            tick_id=self.tick_id,
            plant=self.plant_id,
            amrs=[amr.get_state() for amr in self.amrs],
            lines=self.generator.get_snapshot(),
            obstacles=self.obstacle_manager.get_snapshot(),
            kpis=self.metrics.get_snapshot(),
            notices=self.notices,
            out_stock=dict(self.out_stock)
        )

sim_env = SimulationEnvironment()
