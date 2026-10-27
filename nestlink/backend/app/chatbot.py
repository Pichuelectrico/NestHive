"""Deterministic, read-only operational questions for the NestHive demo."""
from datetime import datetime, timezone
from typing import Any, Dict, List

QUESTIONS = [
    "¿Cuál es el estado de la flota?", "¿Cómo están las baterías?",
    "¿Qué misiones están en curso?", "¿Cuál es el cuello de botella ahora mismo?",
    "¿Cuál es la próxima parada de línea por stock bajo?", "¿Cómo va el turno?",
    "¿Qué incidencias ocurrieron en la última hora?", "¿Cuál es la estrategia actual del orquestador?",
    "¿Qué misiones se completaron en la última hora?", "¿Qué riesgo debo vigilar ahora?",
]

def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()

def asks() -> List[Dict[str, Any]]:
    return [{"id": i + 1, "question": q} for i, q in enumerate(QUESTIONS)]

def answer(q: str, env: Any) -> Dict[str, Any]:
    s = q.lower()
    fleet = [a.get_state().model_dump() for a in env.amrs]
    missions = [m.model_dump() for m in env.mission_queue.get_all_missions()]
    k = env.metrics.get_snapshot().model_dump()
    active = [m for m in missions if m["estado"] in ("asignada", "en_curso")]
    pending = [m for m in missions if m["estado"] == "pendiente"]
    if any(x in s for x in ("bater", "carga")):
        data = {"fleet": [{"id": a["id"], "bateria": a["bateria"], "estado": a["estado"]} for a in fleet]}
        text = "Baterías: " + ", ".join(f'{a["id"]} {a["bateria"]}%' for a in fleet)
    elif any(x in s for x in ("flota", "amr")):
        counts = {}
        for a in fleet: counts[a["estado"]] = counts.get(a["estado"], 0) + 1
        data, text = {"counts": counts, "fleet": fleet}, "Flota híbrida de 6 vehículos: 4 AGVs + 2 AMRs de apoyo en puntos críticos. " + ", ".join(f"{n} {v}" for n, v in counts.items())
    elif any(x in s for x in ("misiones", "misión", "curso", "complet")):
        data = {"active": active, "pending": pending, "completed": [m for m in missions if m["estado"] == "completada"]}
        text = f"{len(active)} misiones en curso y {len(pending)} pendientes; {k['viajes_completados']} viajes completados."
    elif any(x in s for x in ("incid", "riesgo")):
        data = {"notices": [n.model_dump() for n in env.notices]}
        text = data["notices"][-1]["mensaje"] if data["notices"] else "Sin incidencias activas en la ventana reciente."
    elif any(x in s for x in ("turno", "kpi", "va")):
        data, text = {"kpis": k}, f"Turno: {k['viajes_completados']} viajes, {k['paradas_evitadas']} paradas evitadas y {k['km_evitados']} km evitados."
    elif any(x in s for x in ("estrateg", "asignó", "asigno")):
        data = {"active": active, "rule": "prioridad + distancia + afinidad de zona (asignación húngara)"}
        text = "Estrategia activa: prioriza urgencia, distancia y afinidad de zona; la reserva AGV 6 atiende entregas."
    elif any(x in s for x in ("cuello", "parada", "stock")):
        data = {"pending": pending, "lines": env.get_snapshot().model_dump().get("lines", [])}
        text = "Vigilo la cola de misiones y las líneas con menor nivel de material; no hay parada confirmada." if not pending else f"La cola tiene {len(pending)} misiones pendientes; esa es la prioridad operativa."
    else:
        data, text = {"kpis": k, "fleet": fleet, "active_missions": active}, "Estado operativo consultado desde el gemelo en tiempo real."
    return {"answer": text, "data": data, "ts": _ts()}

def hourly_report(env: Any, previous: Dict[str, Any] | None = None) -> Dict[str, Any]:
    k = env.metrics.get_snapshot().model_dump()
    old = (previous or {}).get("kpis", {})
    delta = {name: k.get(name, 0) - old.get(name, 0) for name in ("viajes_completados", "paradas_evitadas", "km_evitados")}
    fleet = [a.get_state().model_dump() for a in env.amrs]
    return {"event": "hourly_report_ready", "sim_hour": int(env.sim_time // 3600), "ts": _ts(), "movements": delta["viajes_completados"], "pallets_delivered": delta["viajes_completados"], "incidents": len(env.notices), "fleet": fleet, "kpis": k, "delta": delta}
