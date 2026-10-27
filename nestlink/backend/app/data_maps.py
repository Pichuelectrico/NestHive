# app/data_maps.py
# Carga y gestión del grafo canónico de la planta con NetworkX y multi-planta

import json
import os
import networkx as nx
from typing import Dict, Any, Tuple

MAPS_DIR = os.path.join(os.path.dirname(__file__), "data", "maps")
SEEDS_DIR = os.path.join(os.path.dirname(__file__), "data", "seeds")

# Planta por defecto del demo (realistic = mapa Nestlé con LiDAR + AMRs rojos)
DEFAULT_PLANT_ID: str = "realistic"

PLANT_CONFIGS = {
    "quito": {
        "id": "quito",
        "nombre": "Planta Quito",
        "map_file": "plant_layout.json",
        "seed_file": "seed.json"
    },
    "realistic": {"id": "realistic", "nombre": "Planta Realistic", "map_file": "realistic.json", "seed_file": "seed_realistic.json"},
    "cd_guayaquil": {
        "id": "cd_guayaquil",
        "nombre": "CD Guayaquil",
        "map_file": "cd_guayaquil.json",
        "seed_file": "seed_guayaquil.json"
    }
}

def load_layout_raw(plant_id: str = DEFAULT_PLANT_ID) -> Dict[str, Any]:
    cfg = PLANT_CONFIGS.get(plant_id, PLANT_CONFIGS[DEFAULT_PLANT_ID])
    file_path = os.path.join(MAPS_DIR, cfg["map_file"])
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_seeds_raw(plant_id: str = DEFAULT_PLANT_ID) -> Dict[str, Any]:
    cfg = PLANT_CONFIGS.get(plant_id, PLANT_CONFIGS[DEFAULT_PLANT_ID])
    file_path = os.path.join(SEEDS_DIR, cfg["seed_file"])
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _seg_intersects(a, b, c, d):
    def ccw(p1, p2, p3):
        return (p3[1]-p1[1])*(p2[0]-p1[0]) - (p2[1]-p1[1])*(p3[0]-p1[0])
    tol=1e-9
    def on(p1,p2,p3):
        return min(p1[0],p2[0])-tol <= p3[0] <= max(p1[0],p2[0])+tol and min(p1[1],p2[1])-tol <= p3[1] <= max(p1[1],p2[1])+tol
    d1,d2 = ccw(c,d,a), ccw(c,d,b)
    d3,d4 = ccw(a,b,c), ccw(a,b,d)
    if ((d1>0 and d2<0) or (d1<0 and d2>0)) and ((d3>0 and d4<0) or (d3<0 and d4>0)):
        return True
    if abs(d1)<tol and on(c,d,a): return True
    if abs(d2)<tol and on(c,d,b): return True
    if abs(d3)<tol and on(a,b,c): return True
    if abs(d4)<tol and on(a,b,d): return True
    return False

def edge_crosses_wall(u_pos, v_pos, walls, node_positions=None):
    return _edge_crosses_walls(u_pos, v_pos, walls)

def _edge_crosses_walls(u_pos, v_pos, walls):
    for w in walls:
        # inflar 0.5px para que toque borde = bloqueado
        pad=0.5
        x,y,w_,h_=w["x"]-pad,w["y"]-pad,w["w"]+2*pad,w["h"]+2*pad
        rect=[(x,y),(x+w_,y),(x+w_,y+h_),(x,y+h_)]
        for i in range(4):
            if _seg_intersects(rect[i], rect[(i+1)%4], u_pos, v_pos):
                return True
        if x < u_pos[0] < x+w_ and y < u_pos[1] < y+h_:
            return True
        if x < v_pos[0] < x+w_ and y < v_pos[1] < y+h_:
            return True
    return False

def build_plant_graph(layout_data: Dict[str, Any]) -> Tuple[nx.DiGraph, Dict[str, Tuple[float, float]]]:
    G = nx.DiGraph()
    node_positions = {}

    for node in layout_data.get("nodes", []):
        nid = node["id"]
        pos = (float(node["x"]), float(node["y"]))
        node_positions[nid] = pos
        G.add_node(
            nid,
            x=pos[0],
            y=pos[1],
            type=node.get("type", "cruce"),
            label=node.get("label", nid)
        )

    walls = layout_data.get("walls", [])
    for edge in layout_data.get("edges", []):
        u = edge["from"]
        v = edge["to"]
        if u not in node_positions or v not in node_positions:
            continue
        if walls and _edge_crosses_walls(node_positions[u], node_positions[v], walls):
            continue
        length = float(edge.get("length", 10.0))
        max_speed = float(edge.get("max_speed", 1.5))
        direction = edge.get("direction", "bi")
        blocked = bool(edge.get("blocked", False))
        weight = length / max(max_speed, 0.1)

        G.add_edge(u, v, length=length, max_speed=max_speed, weight=weight, blocked=blocked, direction=direction)
        if direction == "bi":
            G.add_edge(v, u, length=length, max_speed=max_speed, weight=weight, blocked=blocked, direction=direction)

    return G, node_positions
