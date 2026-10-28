"""ESPOL: la cinta es implícita y la exportación la opera una flota AGV."""

from app.sim.env import SimulationEnvironment


def test_supply_delivery_starts_delayed_recovery_request():
    env = SimulationEnvironment("espol_fusion")
    assert [(line.id, line.nombre) for line in env.generator.lines] == [
        ("R1", "R1 · Cookies"), ("R2", "R2 · Chocolates"), ("R3", "R3 · Wafer")
    ]
    assert [env.generator.espol_supply_destination(f"R{i}") for i in range(1, 4)] == [
        f"INSUMO_P{i}" for i in range(1, 4)
    ]
    initial = env.mission_queue.get_all_missions()
    assert {(m.origen, m.destino) for m in initial} == {
        ("FUENTE_INSUMOS", f"INSUMO_P{i}") for i in range(1, 4)
    }
    assert all(m.tipo == "SUPPLY_REQUEST" for m in initial)

    before = env.generator.lines[1].nivel_pct
    env.generator.supply_delivered("INSUMO_P2", 10.0)
    assert env.get_snapshot().station_stock["INSUMO_P2"] == 3  # 3 generaciones de pallets por insumo
    assert env.get_snapshot().station_stock["RECO_R2"] == 0
    assert env.generator.lines[1].nivel_pct == min(100.0, before + 20.0)
    env.generator.step(19.9, env.mission_queue, 29.9, env.metrics)
    assert not any(m.origen == "RECO_R2" for m in env.mission_queue.get_all_missions())
    env.generator.step(0.1, env.mission_queue, 30.0, env.metrics)
    assert env.get_snapshot().station_stock["INSUMO_P2"] == 2
    assert env.get_snapshot().station_stock["RECO_R2"] == 1
    recovery = [m for m in env.mission_queue.get_all_missions() if m.origen == "RECO_R2"]
    assert len(recovery) == 1
    assert recovery[0].tipo == "PICKUP_PT"
    assert recovery[0].destino.startswith("PALET_")
    assert not any(m.origen == "INSUMO_P2" for m in env.mission_queue.get_all_missions())
    level = env.generator.lines[1].nivel_pct
    env.generator.drain_line_pickup("RECO_R2")
    assert env.get_snapshot().station_stock["RECO_R2"] == 0
    assert abs(env.generator.lines[1].nivel_pct - (level - 20.0 / 3)) < 1e-9


def test_palet_arrival_creates_export_for_dedicated_agv():
    env = SimulationEnvironment("espol_fusion")
    assert {v.clase for v in env.amrs} == {"AGV"}
    assert len(env.amrs) == 5
    assert sum(v.id not in env.delivery_amr_ids and v.id not in env.backup_amr_ids for v in env.amrs) == 3
    assert env.delivery_amr_ids == {"AMR_03"}
    assert env.backup_amr_ids == {"AMR_04"}
    assert next(v for v in env.amrs if v.id == "AMR_04").nombre == "AMR Backup"
    env.out_arrive("PALET_01", 10.0)
    assert env.get_snapshot().out_stock["PALET_01"] == 1
    env._dispatch_exports()
    exports = [m for m in env.mission_queue.get_all_missions() if m.tipo == "EXPORT"]
    assert len(exports) == 1
    assert (exports[0].origen, exports[0].destino) == ("PALET_01", "TRANSPORTE")
    assert exports[0].amr_asignado == "AMR_03"
    env.out_pickup("PALET_01")
    assert env.get_snapshot().out_stock["PALET_01"] == 0


def test_other_agv_assists_only_on_export_overload():
    env = SimulationEnvironment("espol_fusion")
    env.out_arrive("PALET_01", 0.0)
    env.out_arrive("PALET_02", 0.0)
    env._dispatch_exports()
    exports = [m for m in env.mission_queue.get_all_missions() if m.tipo == "EXPORT"]
    assert sum(m.estado == "asignada" for m in exports) == 1
    assert next(m for m in exports if m.estado == "asignada").amr_asignado == "AMR_03"
    env.out_arrive("PALET_03", 0.0)
    env._dispatch_exports()
    assigned = [m for m in env.mission_queue.get_all_missions() if m.tipo == "EXPORT" and m.estado == "asignada"]
    assert len(assigned) >= 2
    assert any(m.amr_asignado != "AMR_03" for m in assigned)


def test_backup_stays_idle_until_primary_breakdown():
    env = SimulationEnvironment("espol_fusion")
    backup = next(v for v in env.amrs if v.id == "AMR_04")
    for _ in range(20):
        env.step_tick()
    assert backup.estado == "IDLE"
    assert not env._backup_needed()
    env.maintenance_broken["AMR_01"] = {"repair_at": env.sim_time + 30, "edge": []}
    assert env._backup_needed()
    assert backup.id in env.backup_amr_ids
    env.step_tick()
    assert backup.tarea_actual is not None
    assert backup.estado == "MOVING_TO_PICKUP"


def test_full_chain_and_realistic_remains_active():
    env = SimulationEnvironment("espol_fusion")
    for _ in range(3000):
        env.step_tick()
    missions = env.mission_queue.get_all_missions()
    completed = [m for m in missions if m.estado == "completada"]
    assert any(m.tipo == "SUPPLY_REQUEST" and m.destino.startswith("INSUMO_P") for m in completed)
    assert any(m.tipo == "PICKUP_PT" and m.origen.startswith("RECO_R") and
               m.destino.startswith("PALET_") for m in completed)
    assert any(m.tipo == "EXPORT" and m.destino == "TRANSPORTE" for m in completed)
    assert all(m.origen == "FUENTE_INSUMOS" and m.destino in
               {"INSUMO_P1", "INSUMO_P2", "INSUMO_P3"}
               for m in missions if m.tipo == "SUPPLY_REQUEST")
    assert not any(m.tipo == "EXPEDITION" for m in missions)

    realistic = SimulationEnvironment("realistic")
    assert not realistic.espol_flow
    assert all(m.origen.startswith("WH_MP_") for m in realistic.mission_queue.get_all_missions())
