# Simulación de operarios peatonales (zonas de seguridad) y bloqueos dinámicos

import math
from typing import List, Dict, Tuple, Optional, Any
from app.models import ObstaculoState
from app.data_maps import build_plant_graph, _edge_crosses_walls


def _safe_route(waypoints: List[str], G, node_positions: Dict[str, Tuple[float, float]],
                walls: List[Dict[str, Any]]) -> List[str]:
    """Convierte una lista de waypoints en una ruta CÍCLICA de nodos conectada por
    aristas del grafo filtrado (G, que ya excluye toda arista que cruce una pared).
    Así el peatón NUNCA camina en línea recta a través de un muro:
      - Si hay camino en G entre waypoint(a) y waypoint(b), se insertan los nodos intermedios.
      - Si no hay camino (a desconectado de b), se omite el salto directo (seguro).
      - La ruta cierra el ciclo: último nodo -> primer waypoint.
    """
    if not waypoints:
        return []
    if len(waypoints) == 1:
        return [waypoints[0]]

    def _path(a: str, b: str):
        if G is None or a not in G or b not in G:
            return None
        try:
            import networkx as nx
            return nx.shortest_path(G, a, b)
        except Exception:
            return None

    route: List[str] = [waypoints[0]]
    # recorremos pares consecutivos + cierre (último -> primero)
    pairs = list(zip(waypoints, waypoints[1:])) + [(waypoints[-1], waypoints[0])]
    for a, b in pairs:
        if a == b:
            continue
        path = _path(a, b)
        if path and len(path) >= 2:
            # añadir los nodos intermedios sin duplicar el de unión
            route.extend(path[1:])
        # si no hay camino por G (desconexo, no debería ocurrir en realistic),
        # no añadimos nada: el peatón se queda en nodos alcanzables -> nunca cruza muro
    # compactar waypoints repetidos consecutivos
    compact = []
    for n in route:
        if not compact or compact[-1] != n:
            compact.append(n)
    return compact


class PedestrianAgent:
    def __init__(self, id_str: str, name: str, waypoints: List[str], speed: float = 1.0, radius: float = 2.5,
                 node_positions: Dict[str, Tuple[float, float]] = None,
                 walls: List[Dict[str, Any]] = None, route: Optional[List[str]] = None):
        self.id = id_str
        self.name = name
        self.speed = speed  # m/s
        self.radius = radius  # metros de seguridad
        self.node_positions = node_positions or {}
        self.walls = walls or []
        # Ruta segura: secuencia de nodos conectados por aristas que no cruzan muros
        self.route = route if route is not None else _safe_route(waypoints, None, self.node_positions, self.walls)
        self.waypoints = waypoints

        self.current_idx = 0
        if self.route and self.route[0] in self.node_positions:
            self.x, self.y = self.node_positions[self.route[0]]
        else:
            self.x, self.y = (400.0, 220.0)

    def step(self, dt: float):
        if not self.route or len(self.route) < 2:
            return

        target_node = self.route[self.current_idx]
        tx, ty = self.node_positions.get(target_node, (self.x, self.y))

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        step_dist = self.speed * 10.0 * dt  # 10 px = 1m

        if dist <= step_dist:
            self.x = tx
            self.y = ty
            self.current_idx = (self.current_idx + 1) % len(self.route)
        else:
            nx = self.x + (dx / dist) * step_dist
            ny = self.y + (dy / dist) * step_dist
            # Clamp defensivo anti-pared: si el tramo cruzara un muro no avanzar.
            # La ruta ya es segura (aristas de G), esto es una red de seguridad.
            if not _edge_crosses_walls((self.x, self.y), (nx, ny), self.walls):
                self.x, self.y = nx, ny


class ObstacleManager:
    def __init__(self, layout_data: Dict[str, Any], node_positions: Dict[str, Tuple[float, float]]):
        self.node_positions = node_positions
        self.pedestrians: List[PedestrianAgent] = []
        self.blocked_edges: Dict[Tuple[str, str], str] = {}  # {(u, v): tipo_obstaculo}

        walls = layout_data.get("walls", [])
        # Grafo filtrado (sin aristas que crucen muros) para rutas peatonales seguras
        try:
            G, _ = build_plant_graph(layout_data)
        except Exception:
            G = None

        for ped in layout_data.get("pedestrians", []):
            wps = ped.get("waypoints", [])
            route = _safe_route(wps, G, node_positions, walls)
            self.pedestrians.append(
                PedestrianAgent(
                    id_str=ped["id"],
                    name=ped.get("name", ped["id"]),
                    waypoints=wps,
                    speed=float(ped.get("speed", 1.0)),
                    radius=float(ped.get("radius", 2.5)),
                    node_positions=node_positions,
                    walls=walls,
                    route=route
                )
            )

    def _recompute_routes(self, layout_data: Dict[str, Any]):
        """Reconstruye rutas seguras tras un cambio de muros (p.ej. actualización del layout)."""
        walls = layout_data.get("walls", [])
        try:
            G, _ = build_plant_graph(layout_data)
        except Exception:
            G = None
        self.walls = walls
        for ped in self.pedestrians:
            ped.walls = walls
            ped.route = _safe_route(ped.waypoints, G, self.node_positions, walls)
            ped.current_idx = 0

    def step(self, dt: float):
        for ped in self.pedestrians:
            ped.step(dt)

    def add_block(self, u: str, v: str, tipo: str = "SPILL"):
        self.blocked_edges[(u, v)] = tipo
        self.blocked_edges[(v, u)] = tipo

    def remove_block(self, u: str, v: str):
        self.blocked_edges.pop((u, v), None)
        self.blocked_edges.pop((v, u), None)

    def get_snapshot(self) -> List[ObstaculoState]:
        obs_list = []
        # Peatones
        for ped in self.pedestrians:
            obs_list.append(
                ObstaculoState(
                    id=ped.id,
                    tipo="OPERATOR",
                    x=round(ped.x, 1),
                    y=round(ped.y, 1),
                    radius=ped.radius,
                    edge=None
                )
            )
        # Bloqueos de aristas
        seen = set()
        for (u, v), tipo in self.blocked_edges.items():
            pair = tuple(sorted([u, v]))
            if pair in seen:
                continue
            seen.add(pair)
            pu = self.node_positions.get(u, (0.0, 0.0))
            pv = self.node_positions.get(v, (0.0, 0.0))
            mid_x = (pu[0] + pv[0]) / 2.0
            mid_y = (pu[1] + pv[1]) / 2.0
            obs_list.append(
                ObstaculoState(
                    id=f"BLK_{u}_{v}",
                    tipo=tipo,
                    x=round(mid_x, 1),
                    y=round(mid_y, 1),
                    radius=0.0,
                    edge=[u, v]
                )
            )
        return obs_list
