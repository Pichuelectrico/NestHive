# app/sim/amr_yield.py
# Módulo de detección y resolución determinista de conflictos AMR<->AMR (cabeceo)

import math
from typing import List, Tuple, Optional, Dict, Any
from app.sim.routing import find_shortest_path_excluding_edge

def get_active_edge(amr: Any) -> Optional[Tuple[str, str]]:
    """Devuelve la arista dirigida activa (u, v) que el AMR está recorriendo."""
    if amr.estado not in ["MOVING_TO_PICKUP", "MOVING_TO_DELIVERY", "REROUTING"]:
        return None
    if not amr.path or amr.target_node_idx >= len(amr.path):
        return None
    to_node = amr.path[amr.target_node_idx]
    from_node = amr.path[amr.target_node_idx - 1] if amr.target_node_idx > 0 else amr.posicion_nodo
    if from_node == to_node:
        return None
    return (from_node, to_node)

def edge_progress(amr: Any, node_positions: Dict[str, Tuple[float, float]]) -> float:
    """Retorna el progreso en la arista activa en rango [0.0, 1.0]."""
    edge = get_active_edge(amr)
    if not edge:
        return 0.0
    from_node, to_node = edge
    fx, fy = node_positions.get(from_node, (amr.x, amr.y))
    tx, ty = node_positions.get(to_node, (amr.x, amr.y))
    edge_len_px = math.hypot(tx - fx, ty - fy)
    if edge_len_px == 0:
        return 1.0
    dist_remaining_px = math.hypot(tx - amr.x, ty - amr.y)
    progress = 1.0 - (dist_remaining_px / edge_len_px)
    return max(0.0, min(1.0, progress))

def remaining_path_distance_m(amr: Any, node_positions: Dict[str, Tuple[float, float]]) -> float:
    """Calcula la distancia restante en metros a lo largo del path del AMR."""
    if not amr.path or amr.target_node_idx >= len(amr.path):
        return 0.0
    
    # Distancia al primer nodo destino
    target_node = amr.path[amr.target_node_idx]
    tx, ty = node_positions.get(target_node, (amr.x, amr.y))
    dist_px = math.hypot(tx - amr.x, ty - amr.y)
    
    # Distancia a través de nodos restantes
    for i in range(amr.target_node_idx, len(amr.path) - 1):
        u, v = amr.path[i], amr.path[i + 1]
        ux, uy = node_positions.get(u, (0.0, 0.0))
        vx, vy = node_positions.get(v, (0.0, 0.0))
        dist_px += math.hypot(vx - ux, vy - uy)
        
    return dist_px / 10.0

def detect_head_on_pairs(
    amrs: List[Any],
    node_positions: Dict[str, Tuple[float, float]],
    lookahead_sec: float = 1.6,
    conflict_radius_m: float = 2.5
) -> List[Tuple[Any, Any]]:
    """Identifica pares de AMRs en conflicto cabeceo (misma arista, direcciones opuestas)."""
    active_amrs = [a for a in amrs if get_active_edge(a) is not None]
    conflicts = []
    
    for i in range(len(active_amrs)):
        for j in range(i + 1, len(active_amrs)):
            a, b = active_amrs[i], active_amrs[j]
            edge_a = get_active_edge(a)
            edge_b = get_active_edge(b)
            
            if not edge_a or not edge_b:
                continue
                
            # Conflicto solo si son direcciones opuestas en la misma arista física (u<->v)
            if edge_a[0] == edge_b[1] and edge_a[1] == edge_b[0]:
                prog_a = edge_progress(a, node_positions)
                prog_b = edge_progress(b, node_positions)
                
                # Si alguno ya completó el tramo (>= 0.95), ya liberó el cabeceo
                if prog_a >= 0.95 or prog_b >= 0.95:
                    continue
                    
                conflicts.append((a, b))
                    
    return conflicts

def pick_winner(a: Any, b: Any, node_positions: Dict[str, Tuple[float, float]]) -> Tuple[Any, Any]:
    """Determina deterministamente cuál AMR tiene prioridad y cuál cede."""
    prio_a = a.tarea_actual.prioridad if a.tarea_actual else 0
    prio_b = b.tarea_actual.prioridad if b.tarea_actual else 0
    
    if prio_a != prio_b:
        return (a, b) if prio_a > prio_b else (b, a)
        
    dist_rem_a = remaining_path_distance_m(a, node_positions)
    dist_rem_b = remaining_path_distance_m(b, node_positions)
    
    if abs(dist_rem_a - dist_rem_b) > 0.1:
        return (a, b) if dist_rem_a < dist_rem_b else (b, a)
        
    # Tie-break por ID lexicográfico menor
    return (a, b) if a.id < b.id else (b, a)

class AmrYieldResolver:
    @staticmethod
    def resolve_amr_conflicts(env: Any, dt_sim: float):
        """Ejecuta la resolución determinista de cesión y re-ruteo antes de la cinemática de los AMRs."""
        sorted_amrs = sorted(env.amrs, key=lambda a: a.id)
        lookahead_sec = 2.0 * dt_sim
        conflicts = detect_head_on_pairs(sorted_amrs, env.node_positions, lookahead_sec=lookahead_sec)
        
        # Mantener registro de AMRs involucrados en conflicto activo este tick
        yielding_losers = set()
        
        for a, b in conflicts:
            winner, loser = pick_winner(a, b, env.node_positions)
            
            if loser.estado not in ["MOVING_TO_PICKUP", "MOVING_TO_DELIVERY", "REROUTING", "WAITING_OBSTACLE"]:
                continue
                
            yielding_losers.add(loser.id)
            active_edge = get_active_edge(loser)
            if not active_edge:
                continue
                
            u, v = active_edge
            prog = edge_progress(loser, env.node_positions)
            
            # Si el perdedor está al inicio de la arista (< 0.05), intentar re-ruteo A* por arista alternativa
            dest = loser.tarea_actual.destino if (loser.tarea_actual and loser.tarea_actual.estado == "en_curso") else (loser.tarea_actual.origen if loser.tarea_actual else loser.path[-1])
            
            alt_path = None
            if prog < 0.05:
                alt_path = find_shortest_path_excluding_edge(env.G, loser.posicion_nodo, dest, env.node_positions, (u, v))
                
            if alt_path and len(alt_path) > 1:
                loser.path = alt_path
                loser.target_node_idx = 1
                loser.estado = "REROUTING"
                if hasattr(loser, "cediendo_paso"):
                    loser.cediendo_paso = False
                env.add_notice("INFO", None, f"Re-ruteo por conflicto: {loser.nombre} cede paso a {winner.nombre}")
            else:
                loser.estado = "WAITING_OBSTACLE"
                if hasattr(loser, "cediendo_paso"):
                    loser.cediendo_paso = True
                env.add_notice("INFO", None, f"{loser.nombre} cediendo paso a {winner.nombre}")

        # Liberar AMRs que estaban cediendo paso y cuyo conflicto ya se resolvió
        for amr in env.amrs:
            if getattr(amr, "cediendo_paso", False) and amr.id not in yielding_losers:
                amr.cediendo_paso = False
                if amr.estado == "WAITING_OBSTACLE":
                    amr.estado = "MOVING_TO_DELIVERY" if (amr.tarea_actual and amr.tarea_actual.estado == "en_curso") else "MOVING_TO_PICKUP"

