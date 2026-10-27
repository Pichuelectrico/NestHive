# app/sim/routing.py
# Motor de ruteo A* dinámico sobre el grafo de la planta con manejo de bloqueos

import math
import networkx as nx
from typing import List,Dict,Tuple,Optional,Any

def euclidean_heuristic(u: str, v: str, node_positions: Dict[str, Tuple[float, float]]) -> float:
    pos_u = node_positions.get(u, (0.0, 0.0))
    pos_v = node_positions.get(v, (0.0, 0.0))
    # Retorna distancia estimada / velocidad máx (1.8 m/s) en escala métrica (10px = 1m)
    dx = (pos_u[0] - pos_v[0]) / 10.0
    dy = (pos_u[1] - pos_v[1]) / 10.0
    return math.sqrt(dx * dx + dy * dy) / 1.8

def get_free_buffer_for_line(
    G: nx.DiGraph,
    layout: dict,
    line_id: str,
    busy_nodes: set
) -> Optional[str]:
    """
    Devuelve el primer nodo type=="buffer" de layout['lines'][line_id]['buffer_nodes']
    que NO esté en busy_nodes (orden estable).
    """
    lines = layout.get("lines", [])
    target_line = None
    for line in lines:
        if line.get("id") == line_id:
            target_line = line
            break
    if not target_line:
        return None

    buffer_nodes = target_line.get("buffer_nodes", [])
    for b_node in buffer_nodes:
        if b_node not in busy_nodes:
            # Confirm standard node type if exists in G
            if G.has_node(b_node):
                if G.nodes[b_node].get("type") == "buffer":
                    return b_node
            else:
                return b_node
    return None

def find_shortest_path(
    G: nx.DiGraph,
    source: str,
    target: str,
    node_positions: Dict[str, Tuple[float, float]],
    avoid_opposite: Optional[Any] = None
) -> Optional[List[str]]:
    """
    Encuentra la ruta A* más corta entre dos nodos ignorando aristas bloqueadas.
    Soporta avoid_opposite: callable (u, v) -> bool. Si es True, penaliza la arista.
    """
    if source == target:
        return [source]

    def weight_func(u, v, data):
        if data.get("blocked", False):
            return None  # Inaccesible
        base_w = data.get("weight", 1.0)
        if avoid_opposite and avoid_opposite(u, v):
            base_w += 1000.0  # Penalización alta para evitar aristas reservadas en sentido opuesto
        return base_w

    try:
        path = nx.astar_path(
            G,
            source,
            target,
            heuristic=lambda u, v: euclidean_heuristic(u, v, node_positions),
            weight=weight_func
        )
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def block_edge(G: nx.DiGraph, u: str, v: str) -> bool:
    """Marca la arista (u, v) y su contraparte (v, u) como bloqueada."""
    changed = False
    if G.has_edge(u, v):
        G[u][v]["blocked"] = True
        changed = True
    if G.has_edge(v, u):
        G[v][u]["blocked"] = True
        changed = True
    return changed

def unblock_edge(G: nx.DiGraph, u: str, v: str) -> bool:
    """Restaura la arista (u, v) y su contraparte (v, u)."""
    changed = False
    if G.has_edge(u, v):
        G[u][v]["blocked"] = False
        changed = True
    if G.has_edge(v, u):
        G[v][u]["blocked"] = False
        changed = True
    return changed

def find_shortest_path_excluding_edge(
    G: nx.DiGraph,
    source: str,
    target: str,
    node_positions: Dict[str, Tuple[float, float]],
    exclude_edge: Tuple[str, str]
) -> Optional[List[str]]:
    """
    Encuentra la ruta A* omitiendo la orientación u->v de exclude_edge.
    Respetando la dirección si es unidireccional.
    No muta el grafo G global.
    """
    if source == target:
        return [source]

    u_ex, v_ex = exclude_edge

    def weight_func(u, v, data):
        if data.get("blocked", False):
            return None
        if u == u_ex and v == v_ex:
            return None
        return data.get("weight", 1.0)

    try:
        path = nx.astar_path(
            G,
            source,
            target,
            heuristic=lambda u, v: euclidean_heuristic(u, v, node_positions),
            weight=weight_func
        )
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

