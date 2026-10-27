# app/sim/assignment.py
# Cola de misiones priorizada y asignador global óptimo (Método Húngaro con afinidad)

import math
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Tuple, Dict, Optional, Any
from app.models import Tarea

class MissionQueue:
    def __init__(self):
        self.missions: List[Tarea] = []
        self._counter: int = 1

    def add_mission(
        self,
        tipo: str,
        origen: str,
        destino: str,
        prioridad: int = 5,
        peso_kg: float = 100.0,
        sim_time: float = 0.0,
        force_urgent: bool = False
    ) -> Tarea:
        task_id = f"TSK_{self._counter:03d}"
        self._counter += 1
        prio = prioridad
        mission = Tarea(
            id=task_id,
            tipo=tipo,
            origen=origen,
            destino=destino,
            prioridad=prio,
            peso_kg=peso_kg,
            estado="pendiente",
            created_at_sim=sim_time
        )
        self.missions.append(mission)
        self.missions.sort(key=lambda m: (-m.prioridad, m.created_at_sim))
        return mission

    def get_pending_missions(self) -> List[Tarea]:
        return [m for m in self.missions if m.estado == "pendiente"]

    def get_all_missions(self) -> List[Tarea]:
        return self.missions

def compute_hungarian_assignment(
    idle_amrs: List[Any],
    pending_missions: List[Tarea],
    node_positions: Dict[str, Tuple[float, float]]
) -> List[Tuple[Any, Tarea]]:
    """
    Asigna AMRs libres a misiones pendientes usando el Método Húngaro (Scipy)
    incorporando afinidad de zona (home-zone) para que la flota sea coherente y activa.
    """
    if not idle_amrs or not pending_missions:
        return []

    num_amrs = len(idle_amrs)
    num_tasks = len(pending_missions)
    cost_matrix = np.zeros((num_amrs, num_tasks))

    for i, amr in enumerate(idle_amrs):
        for j, task in enumerate(pending_missions):
            target_pos = node_positions.get(task.origen, (amr.x, amr.y))
            dx = amr.x - target_pos[0]
            dy = amr.y - target_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)

            # Factor de prioridad (10 = crítico reduce costo)
            prio_factor = 1.0 / max(task.prioridad, 1)

            # Factor de afinidad / Home Zone
            affinity_factor = 1.0
            if amr.home_zone:
                if amr.home_zone in [task.origen, task.destino]:
                    affinity_factor = 0.35  # Gran incentivo para su línea asignada
                else:
                    affinity_factor = 1.25  # Menor preferencia si no es su línea
            else:
                # Comodín (Nestlé Runner): neutral, pero muy veloz para emergencias
                affinity_factor = 0.65 if task.prioridad >= 8 else 0.85

            cost_matrix[i, j] = dist * prio_factor * affinity_factor

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignments = []
    for r, c in zip(row_ind, col_ind):
        assignments.append((idle_amrs[r], pending_missions[c]))

    return assignments
