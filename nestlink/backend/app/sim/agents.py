# app/sim/agents.py
# FSM y cinemática continua de la flota de AMRs Nestlé

import math
import networkx as nx
from typing import List, Tuple, Dict, Any, Optional
from app.models import AMRState, Tarea, EstadoAMR
from app.sim.routing import find_shortest_path

class AMRAgent:
    def __init__(
        self,
        id_str: str,
        nombre: str,
        tipo: str = "pallet_lifter",
        velocidad_ms: float = 1.5,
        carga_kg: float = 500.0,
        bateria_inicial: int = 100,
        posicion_nodo: str = "CHARGER_1",
        home_zone: Optional[str] = None,
        node_positions: Dict[str, Tuple[float, float]] = None,
        node_types: Dict[str, str] = None,
        charger_resolver: Optional[Any] = None
    ):
        self.id = id_str
        self.nombre = nombre
        self.tipo = tipo
        self.velocidad_ms = velocidad_ms
        self.carga_kg = carga_kg
        self.bateria = bateria_inicial
        self.posicion_nodo = posicion_nodo
        self.home_zone = home_zone
        self.node_positions = node_positions or {}
        self.node_types = node_types or {}
        self.charger_resolver = charger_resolver
        self.cediendo_paso = False
        self._estado_desde = 0.0
        self._last_estado = "IDLE" 

        if posicion_nodo in self.node_positions:
            self.x, self.y = self.node_positions[posicion_nodo]
        else:
            self.x, self.y = (400.0, 40.0)

        self.angulo: float = 0.0
        self.estado: EstadoAMR = "IDLE"
        self.tarea_actual: Optional[Tarea] = None
        self.path: List[str] = []
        self.target_node_idx: int = 0
        self.loading_timer: float = 0.0
        self.idle_timer: float = 0.0

    def assign_mission(self, mission: Tarea, G: nx.DiGraph, env: Optional[Any] = None) -> bool:
        """Asigna una misión al AMR. Retorna True si se encontró ruta válida."""
        target_dest = mission.destino if mission.tipo == "RELOCATION" else mission.origen
        avoid_cb = (lambda u, v: any(u == rev_v and v == rev_u for (rev_u, rev_v, exp) in env.edge_reservations)) if (env and hasattr(env, 'edge_reservations')) else None
        calc_path = find_shortest_path(G, self.posicion_nodo, target_dest, self.node_positions, avoid_opposite=avoid_cb)

        if not calc_path:
            # No hay ruta: rechazar misión para que no quede colgada
            return False

        self.tarea_actual = mission
        mission.estado = "asignada"
        mission.amr_asignado = self.id
        self.idle_timer = 0.0
        self.path = calc_path
        if env and hasattr(env, 'reserve_path'):
            env.reserve_path(self, calc_path)
        self.target_node_idx = 1 if len(self.path) > 1 else 0
        if env and hasattr(env, 'sim_time'):
            self._estado_desde = env.sim_time
        self.estado = "MOVING_TO_PICKUP"
        return True

    def step(
        self,
        dt_sim: float,
        G: nx.DiGraph,
        obstacles: List[Any],
        metrics_manager: Any,
        sim_time: float = 0.0,
        generator_manager: Any = None,
        env: Optional[Any] = None
    ):
        estado_previo = self.estado

        # 1. Comprobar proximidad con peatones
        is_blocked_by_pedestrian = False
        for obs in obstacles:
            if obs.tipo == "OPERATOR":
                dx = (obs.x - self.x) / 10.0
                dy = (obs.y - self.y) / 10.0
                dist_m = math.sqrt(dx * dx + dy * dy)
                if dist_m < obs.radius:
                    is_blocked_by_pedestrian = True
                    break

        is_stationary_over_timeout = (env and hasattr(env, '_is_pedestrian_stationary') and env._is_pedestrian_stationary(self, min_seconds=15.0) and (sim_time - getattr(self, "_estado_desde", sim_time)) >= getattr(env, "FREEZE_TIMEOUT_S", 90.0))

        if (is_blocked_by_pedestrian and not is_stationary_over_timeout) or self.cediendo_paso:
            if self.estado in ["MOVING_TO_PICKUP", "MOVING_TO_DELIVERY"]:
                self.estado = "WAITING_OBSTACLE"
            if self.estado != estado_previo:
                self._estado_desde = sim_time
            return
        elif self.estado == "WAITING_OBSTACLE":
            self.estado = "MOVING_TO_DELIVERY" if (self.tarea_actual and self.tarea_actual.estado == "en_curso") else "MOVING_TO_PICKUP"
            self._estado_desde = sim_time

        # 2. FSM Transitions
        if self.estado == "IDLE":
            self.idle_timer += dt_sim

        elif self.estado == "LOADING":
            self.loading_timer -= dt_sim
            if self.loading_timer <= 0:
                if self.tarea_actual:
                    if self.tarea_actual.tipo == "RELOCATION":
                        self.tarea_actual.estado = "completada"
                        self.tarea_actual = None
                        self.estado = "IDLE"
                    else:
                        # Si recogió producto terminado en salida de línea, drenar pallet de la línea
                        if self.tarea_actual.tipo == "PICKUP_PT" and generator_manager:
                            generator_manager.drain_line_pickup(self.tarea_actual.origen, amount_pct=50.0)

                        # Ronda 15 (control de estados OUT): el AMR exclusivo recoge del OUT → el
                        # paquete sale del buffer (emoji 📦 apagado) y viaja al muro en vuelo.
                        if (
                            self.tarea_actual.tipo == "EXPORT"
                            and env
                            and getattr(env, "out_nodes", [])
                            and self.tarea_actual.origen in env.out_nodes
                        ):
                            env.out_pickup(self.tarea_actual.origen, amr_name=self.nombre)

                        self.tarea_actual.estado = "en_curso"
                        avoid_cb = (lambda u, v: any(u == rev_v and v == rev_u for (rev_u, rev_v, exp) in env.edge_reservations)) if (env and hasattr(env, 'edge_reservations')) else None
                        self.path = find_shortest_path(G, self.posicion_nodo, self.tarea_actual.destino, self.node_positions, avoid_opposite=avoid_cb) or [self.posicion_nodo]
                        if env and hasattr(env, 'reserve_path') and len(self.path) > 1:
                            env.reserve_path(self, self.path)
                        self.target_node_idx = 1 if len(self.path) > 1 else 0
                        self.estado = "MOVING_TO_DELIVERY"
                else:
                    self.estado = "IDLE"

        elif self.estado == "UNLOADING":
            self.loading_timer -= dt_sim
            if self.loading_timer <= 0:
                if self.tarea_actual:
                    # Si entregó insumos a empacadora, RESTOCK visible de la línea
                    if self.tarea_actual.tipo == "SUPPLY_REQUEST" and generator_manager:
                        generator_manager.restock_line(self.tarea_actual.destino, amount_pct=20.0)

                    # Ronda 13: Paletizado → OUT. Al entregar PT en Paletizado (WH_PT_*), se
                    # encadena una misión EXPEDITION (WH_PT → OUT<mejor buffer>). Entregar en un
                    # OUT deja el paquete en buffer esperando la entrega exclusiva al muro.
                    if (
                        self.tarea_actual.tipo == "PICKUP_PT"
                        and self.tarea_actual.destino.startswith("WH_PT")
                        and env
                        and getattr(env, "out_nodes", [])
                    ):
                        already_exp = any(
                            m for m in env.mission_queue.get_all_missions()
                            if m.tipo == "EXPEDITION"
                            and m.origen == self.tarea_actual.destino
                            and m.estado in ["pendiente", "asignada", "en_curso"]
                        )
                        if not already_exp:
                            best_out = env.pick_best_out(self.tarea_actual.destino)
                            env.mission_queue.add_mission(
                                tipo="EXPEDITION",
                                origen=self.tarea_actual.destino,
                                destino=best_out,
                                prioridad=6,
                                peso_kg=480.0,
                                sim_time=sim_time
                            )
                            env.add_notice("INFO", None, f"Pallet de {self.tarea_actual.destino} expedido a {best_out} (buffer de entrega)")

                    # Ronda 15 (control de estados OUT): al entregar EXPEDITION en un OUT,
                    # el paquete pasa a "listo en buffer" (out_stock+1 → emoji 📦) y el control
                    # out_arrive provisiona/encadena el EXPORT único hacia el muro.
                    if (
                        self.tarea_actual.tipo == "EXPEDITION"
                        and env
                        and getattr(env, "out_nodes", [])
                        and self.tarea_actual.destino in env.out_nodes
                    ):
                        env.out_arrive(self.tarea_actual.destino, sim_time=sim_time)

                    # Ronda 15: el AMR exclusivo entrega en el muro externo → out_ship embarca,
                    # descuenta la misión programada (contador, sin escaneo de cola) y si aún
                    # queda stock esperando encadena la siguiente EXPORT.
                    if (
                        self.tarea_actual.tipo == "EXPORT"
                        and env
                        and getattr(env, "out_nodes", [])
                        and self.tarea_actual.origen in env.out_nodes
                    ):
                        env.out_ship(self.tarea_actual.origen, amr_name=self.nombre)

                    self.tarea_actual.estado = "completada"
                    duration_min = round((sim_time - self.tarea_actual.created_at_sim) / 60.0, 2)
                    metrics_manager.record_trip_completed(
                        duration_min=max(duration_min, 0.4),
                        distance_km=0.32,
                        was_empty_prevented=True
                    )
                    self.tarea_actual = None
                self.estado = "IDLE"
                self.path = []

        elif self.estado == "CHARGING":
            # REGLA ESTRICTA: Solo cargar si está físicamente en un nodo tipo 'carga'
            is_at_charger = self.node_types.get(self.posicion_nodo) == "carga"
            if not is_at_charger:
                # Si no está en cargador, rutear al destino RECHARGE o resolver — nunca hardcode CHARGER_1
                self.estado = "MOVING_TO_DELIVERY"
                target_ch = self._resolve_charger_target()
                self.path = find_shortest_path(G, self.posicion_nodo, target_ch, self.node_positions) or []
                if self.path:
                    self.target_node_idx = 1 if len(self.path) > 1 else 0
                else:
                    self.estado = "WAITING_OBSTACLE"
            else:
                self.bateria = min(100, int(self.bateria + 4.0 * dt_sim))
                if self.bateria >= 98:
                    self.bateria = 100
                    if self.tarea_actual and self.tarea_actual.tipo == "RECHARGE":
                        self.tarea_actual.estado = "completada"
                        self.tarea_actual = None
                    self.estado = "IDLE"

        elif self.estado in ["MOVING_TO_PICKUP", "MOVING_TO_DELIVERY", "REROUTING"]:
            self._move_along_path(dt_sim, G, env)

    def _move_along_path(self, dt_sim: float, G: nx.DiGraph, env: Optional[Any] = None):
        # Si el estado es REROUTING pero ya tiene un path válido, reanudar movimiento
        if self.estado == "REROUTING" and self.path and self.target_node_idx < len(self.path):
            self.estado = "MOVING_TO_DELIVERY" if (self.tarea_actual and self.tarea_actual.estado == "en_curso") else "MOVING_TO_PICKUP"

        # Consumo de batería: proporcional al tiempo en movimiento (Watt en tránsito)
        self.bateria = max(0.0, self.bateria - 0.10 * dt_sim)

        if not self.path or self.target_node_idx >= len(self.path):
            self.posicion_nodo = self.path[-1] if self.path else self.posicion_nodo
            
            # Al llegar al destino final del path
            if self.tarea_actual and self.tarea_actual.tipo == "RECHARGE":
                # VALIDACIÓN CRÍTICA: Solo pasar a CHARGING si el nodo actual es tipo 'carga'
                if self.node_types.get(self.posicion_nodo) == "carga":
                    self.estado = "CHARGING"
                    self.path = []
                else:
                    target_ch = self._resolve_charger_target()
                    self.path = find_shortest_path(G, self.posicion_nodo, target_ch, self.node_positions) or [self.posicion_nodo]
                    self.target_node_idx = 1 if len(self.path) > 1 else 0
                    self.estado = "MOVING_TO_DELIVERY"
            elif self.estado == "MOVING_TO_PICKUP":
                self.estado = "LOADING"
                self.loading_timer = 2.0
            elif self.estado == "MOVING_TO_DELIVERY":
                self.estado = "UNLOADING"
                self.loading_timer = 2.0
            elif self.estado == "WAITING":
                # Si estaba en WAITING en buffer y la estación destino se desocupó, reanudar
                dest = self.tarea_actual.destino if (self.tarea_actual and self.tarea_actual.estado == "en_curso") else (self.tarea_actual.origen if self.tarea_actual else None)
                if dest and env:
                    other_at_dest = any(a.id != self.id and a.posicion_nodo == dest for a in getattr(env, 'amrs', []))
                    if not other_at_dest:
                        new_path = find_shortest_path(G, self.posicion_nodo, dest, self.node_positions)
                        if new_path and len(new_path) > 1:
                            self.path = new_path
                            self.target_node_idx = 1
                            self.estado = "MOVING_TO_DELIVERY" if (self.tarea_actual and self.tarea_actual.estado == "en_curso") else "MOVING_TO_PICKUP"
            return

        next_node = self.path[self.target_node_idx]
        current_node = self.path[self.target_node_idx - 1] if self.target_node_idx > 0 else self.posicion_nodo

        # Comprobar si el próximo paso es la estación de entrega y está ocupada por otro AMR
        if env and next_node == self.path[-1] and (self.estado in ["MOVING_TO_DELIVERY", "MOVING_TO_PICKUP"]):
            other_amr = next((a for a in getattr(env, 'amrs', []) if a.id != self.id and a.posicion_nodo == next_node), None)
            if other_amr:
                if other_amr.estado == "IDLE":
                    # Si el AMR ocupante está IDLE, forzar su reubicación inmediata
                    target_hub = other_amr.home_zone if (other_amr.home_zone and env.node_types.get(other_amr.home_zone) not in ["linea", "empacadora", "almacen"]) else ("X_02" if "X_02" in self.node_positions else list(self.node_positions.keys())[0])
                    if other_amr.posicion_nodo != target_hub:
                        env.mission_queue.add_mission("RELOCATION", other_amr.posicion_nodo, target_hub, prioridad=4, sim_time=env.sim_time)
                        other_amr.idle_timer = 0.0
                from app.sim.routing import get_free_buffer_for_line
                line_id = None
                if self.tarea_actual:
                    dest_str = self.tarea_actual.destino if self.tarea_actual.estado == "en_curso" else self.tarea_actual.origen
                    if dest_str.startswith("L1") or dest_str.startswith("E1") or "linea1" in dest_str:
                        line_id = "linea1"
                    elif dest_str.startswith("L2") or dest_str.startswith("E2") or "linea2" in dest_str:
                        line_id = "linea2"
                    elif dest_str.startswith("L3") or dest_str.startswith("E3") or "linea3" in dest_str:
                        line_id = "linea3"
                if line_id and hasattr(env, 'layout_raw'):
                    busy_nodes = {a.posicion_nodo for a in getattr(env, 'amrs', [])}
                    free_buf = get_free_buffer_for_line(G, env.layout_raw, line_id, busy_nodes)
                    if free_buf:
                        buf_path = find_shortest_path(G, current_node, free_buf, self.node_positions)
                        if buf_path:
                            self.path = buf_path
                            self.target_node_idx = 1 if len(buf_path) > 1 else 0
                            return
                    else:
                        # Si todos los buffers están ocupados, esperar en la última ranura buffer (o donde esté) sin bloquear cruces
                        self.estado = "WAITING"
                        return

        if G.has_edge(current_node, next_node) and G[current_node][next_node].get("blocked", False):
            dest = self.tarea_actual.destino if (self.tarea_actual and self.tarea_actual.estado == "en_curso") else (self.tarea_actual.origen if self.tarea_actual else self.path[-1])
            new_path = find_shortest_path(G, current_node, dest, self.node_positions)
            if new_path and len(new_path) > 1:
                self.path = new_path
                self.target_node_idx = 1
                self.estado = "MOVING_TO_DELIVERY" if (self.tarea_actual and self.tarea_actual.estado == "en_curso") else "MOVING_TO_PICKUP"
            else:
                self.estado = "REROUTING"
            return

        tx, ty = self.node_positions.get(next_node, (self.x, self.y))
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0.1:
            self.angulo = round(math.degrees(math.atan2(dy, dx)), 1)

        step_dist = self.velocidad_ms * 10.0 * dt_sim

        if dist <= step_dist:
            self.x = tx
            self.y = ty
            self.posicion_nodo = next_node
            self.target_node_idx += 1
        else:
            self.x += (dx / dist) * step_dist
            self.y += (dy / dist) * step_dist

    def _resolve_charger_target(self) -> str:
        """Destino de recarga: misión RECHARGE → resolver → primer cargador del layout."""
        if self.tarea_actual and self.tarea_actual.tipo == "RECHARGE" and self.tarea_actual.destino:
            return self.tarea_actual.destino
        if self.charger_resolver:
            resolved = self.charger_resolver(self.id)
            if resolved:
                return resolved
        chargers = [nid for nid, ntype in self.node_types.items() if ntype == "carga"]
        return chargers[0] if chargers else "CHARGER_1"

    def get_state(self) -> AMRState:
        remaining_path = self.path[self.target_node_idx:] if self.path else []
        return AMRState(
            id=self.id,
            nombre=self.nombre,
            estado=self.estado,
            x=round(self.x, 1),
            y=round(self.y, 1),
            angulo=self.angulo,
            bateria=int(round(self.bateria)),
            tarea_asignada=self.tarea_actual.id if self.tarea_actual else None,
            path=remaining_path,
            tipo=self.tipo,
            cediendo_paso=self.cediendo_paso
        )
