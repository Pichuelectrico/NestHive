# app/sim/assignment.py
# Cola de misiones priorizada y asignador global óptimo (Método Húngaro con afinidad)

import math
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Tuple, Dict, Optional, Any
from app.models import Tarea

POLICY = json.loads((Path(__file__).resolve().parents[1] / "data" / "fleet_policy.json").read_text())

def default_eligible(amr: Any, task: Tarea) -> bool:
    """Fleet-domain gate; conservative defaults preserve legacy callers."""
    clase = getattr(amr, "clase", None)
    if clase not in ("AGV", "AMR"):
        clase = "AMR" if getattr(amr, "id", "") in {"AMR_04", "AMR_05"} else "AGV"
    tipo = task.tipo
    emergency = bool(getattr(task, "emergency", False))
    is_reco = tipo.startswith("RECO_") or getattr(task, "origen", "").startswith("RECO_")
    if tipo in ("RECHARGE", "RELOCATION"):
        return True
    if is_reco:
        return clase == "AGV" or emergency
    if tipo == "PICKUP_PT":
        return clase == "AGV" or emergency
    if tipo in ("EXPORT", "EXPEDITION"):
        return clase in ("AGV", "AMR")
    if tipo == "SUPPLY_REQUEST":
        return clase == "AGV"
    return True

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
    node_positions: Dict[str, Tuple[float, float]],
    eligible: Optional[Any] = None
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
            gate = eligible or default_eligible
            if not gate(amr, task):
                cost_matrix[i, j] = np.inf
                continue
            clase = getattr(amr, "clase", None) or ("AMR" if getattr(amr, "id", "") in {"AMR_04", "AMR_05"} else "AGV")
            if (task.tipo.startswith("RECO_") or task.origen.startswith("RECO_")) and clase == "AMR" and not getattr(task, "emergency", False):
                cost_matrix[i, j] = np.inf
                continue
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

    row_ind, col_ind = linear_sum_assignment(np.where(np.isfinite(cost_matrix), cost_matrix, 1e12))

    assignments = []
    for r, c in zip(row_ind, col_ind):
        if np.isfinite(cost_matrix[r, c]):
            assignments.append((idle_amrs[r], pending_missions[c]))

    return assignments
