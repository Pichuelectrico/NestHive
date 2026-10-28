"""Avería temporal: diagnóstico, cierre de tramo, desvío y pausa real."""

from app.sim.env import SimulationEnvironment
from app.sim.routing import find_shortest_path


def _put_on_edge(env, vehicle, u, v):
    vehicle.posicion_nodo = u
    vehicle.x, vehicle.y = env.node_positions[u]
    vehicle.path = [u, v]
    vehicle.target_node_idx = 1
    vehicle.estado = "MOVING_TO_PICKUP"


def test_software_signal_reports_critical_wear_and_repair_is_ten_sim_seconds():
    env = SimulationEnvironment("espol_fusion")
    vehicle = env.amrs[0]
    assert env.receive_maintenance_signal(vehicle.id, 86.0, None)["status"] == "critical"
    assert any(n.tipo == "MAINTENANCE_PREVENTIVE" for n in env.notices)

    for _ in range(20):
        env.step_tick()
        if vehicle.estado in ("MOVING_TO_PICKUP", "MOVING_TO_DELIVERY") and vehicle.path:
            break
    original_position = (vehicle.x, vehicle.y)
    result = env.receive_maintenance_signal(vehicle.id, None, "llanta")
    assert result["status"] == "broken"
    u, v = result["edge"]
    assert vehicle.estado == "ERROR"
    assert env.G[u][v]["blocked"]
    assert any(o.tipo == "BLOCK" and o.edge == [u, v] or o.edge == [v, u]
               for o in env.obstacle_manager.get_snapshot())
    assert env.get_snapshot().maintenance[0].remaining_seconds == 10.0
    for _ in range(9):
        env.step_tick(1.0)
    assert vehicle.estado == "ERROR"
    assert (vehicle.x, vehicle.y) == original_position
    env.step_tick(1.0)
    assert vehicle.estado != "ERROR"
    assert not env.G[u][v]["blocked"]
    assert env.get_snapshot().maintenance[0].wear_pct == 45.0


def test_other_agv_reroutes_around_damaged_edge():
    env = SimulationEnvironment("espol_fusion")
    candidate = None
    for u, v in env.G.edges():
        if env.node_positions[u] == env.node_positions[v]:
            continue
        path = find_shortest_path(env.G, u, v, env.node_positions)
        env.G[u][v]["blocked"] = env.G[v][u]["blocked"] = True
        alternate = find_shortest_path(env.G, u, v, env.node_positions)
        env.G[u][v]["blocked"] = env.G[v][u]["blocked"] = False
        if path and alternate and len(alternate) > 2:
            candidate = (u, v)
            break
    assert candidate
    u, v = candidate
    damaged, other = env.amrs[:2]
    _put_on_edge(env, damaged, u, v)
    _put_on_edge(env, other, u, v)
    other.x = (env.node_positions[u][0] + env.node_positions[v][0]) / 2
    other.y = (env.node_positions[u][1] + env.node_positions[v][1]) / 2
    result = env.trigger_breakdown(damaged.id)
    assert result["edge"] == [u, v]
    assert not env.maintenance_paused
    other.step(0.8, env.G, [], env.metrics, env.sim_time, env.generator, env)
    assert (other.x == env.node_positions[u][0] or other.y == env.node_positions[u][1])
    for _ in range(10):
        other.step(0.8, env.G, [], env.metrics, env.sim_time, env.generator, env)
    assert other.path[0] == u and other.path[-1] == v
    assert len(other.path) > 2
    assert all(not env.G[a][b]["blocked"] for a, b in zip(other.path, other.path[1:]))


def test_unique_active_route_pauses_operation_until_repair():
    env = SimulationEnvironment("espol_fusion")
    p1 = env.node_positions["INSUMO_P1"]
    edge = next((u, v) for u, v in env.G.edges()
                if env.node_positions[u] == p1 and env.node_positions[v] != p1)
    vehicle = env.amrs[0]
    _put_on_edge(env, vehicle, *edge)
    result = env.trigger_breakdown(vehicle.id)
    assert result["maintenance_paused"]
    assert env.get_snapshot().maintenance_paused
    before = env.tick_id
    positions = [(a.x, a.y) for a in env.amrs]
    env.step_tick(9.0)
    assert env.tick_id == before + 1
    assert [(a.x, a.y) for a in env.amrs] == positions
    env.step_tick(1.0)
    assert not env.maintenance_paused
    assert not env.G[edge[0]][edge[1]]["blocked"]
