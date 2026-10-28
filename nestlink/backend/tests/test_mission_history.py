from app.sim.assignment import MissionQueue


def test_completed_history_is_bounded_and_live_missions_are_preserved():
    queue = MissionQueue()
    pending = queue.add_mission("SUPPLY_REQUEST", "FUENTE_INSUMOS", "INSUMO_P1")
    for index in range(queue.COMPLETED_HISTORY_LIMIT + 1):
        mission = queue.add_mission("PICKUP_PT", f"RECO_{index}", "PALET_01", sim_time=index)
        mission.estado = "completada"
        # Trigger retention after each completion, as the next tick would.
        queue.add_mission("RELOCATION", "X_01", "X_02", sim_time=index).estado = "completada"

    all_missions = queue.get_all_missions()
    completed = [mission for mission in all_missions if mission.estado == "completada"]
    assert len(completed) <= queue.COMPLETED_HISTORY_LIMIT
    assert pending in all_missions

    visible = queue.get_recent_missions(completed_limit=25)
    assert pending in visible
    assert sum(mission.estado == "completada" for mission in visible) == 25

