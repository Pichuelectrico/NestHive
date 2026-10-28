"""Geometry contract shared by ESPOL's API, renderer, and vehicle router."""

import networkx as nx

from app.data_maps import build_plant_graph, edge_crosses_wall, load_layout_raw
from app.sim.routing import find_shortest_path
from app.sim.env import SimulationEnvironment


def test_espol_map_is_one_visible_manhattan_network():
    layout = load_layout_raw("espol_fusion")
    graph, positions = build_plant_graph(layout)

    assert len(positions) == len(layout["nodes"])
    assert nx.is_connected(graph.to_undirected())
    assert "B34" not in positions
    assert not {"B51", "B73", "B74", "B95", "B96", "B98", "B99", "B100", "B101"} & positions.keys()
    assert positions["B97"] == (350.0, 520.0)
    assert positions["J_INSUMOS"] == (400.0, 520.0)
    assert all(f"B{i}" in positions for i in range(102, 110))
    assert positions["TRANSPORTE"][0] < 50
    for edge in layout["edges"]:
        start, end = positions[edge["from"]], positions[edge["to"]]
        assert start[0] == end[0] or start[1] == end[1], edge
        assert graph.has_edge(edge["from"], edge["to"]), edge
        assert not edge_crosses_wall(start, end, layout["walls"]), edge

    for source in ("RECO_R1", "RECO_R2", "RECO_R3"):
        for destination in ("PALET_01", "PALET_08", "PALET_15"):
            route = find_shortest_path(graph, source, destination, positions)
            assert route and "TRANSPORTE" not in route

    for station in ("INSUMO_P1", "INSUMO_P2", "INSUMO_P3"):
        assert find_shortest_path(graph, "FUENTE_INSUMOS", station, positions)
    for station in ("RECO_R3", "INSUMO_P3"):
        assert find_shortest_path(graph, "B21", station, positions)


def test_espol_vehicles_stay_on_visible_edges_through_complete_cycles():
    env = SimulationEnvironment("espol_fusion")
    segments = [(env.node_positions[u], env.node_positions[v]) for u, v in env.G.edges()]

    def on_edge(x, y):
        return any(
            (abs(a[0] - b[0]) < 1e-6 and abs(x - a[0]) < 1e-4 and
             min(a[1], b[1]) - 1e-4 <= y <= max(a[1], b[1]) + 1e-4) or
            (abs(a[1] - b[1]) < 1e-6 and abs(y - a[1]) < 1e-4 and
             min(a[0], b[0]) - 1e-4 <= x <= max(a[0], b[0]) + 1e-4)
            for a, b in segments
        )

    for _ in range(3000):
        env.step_tick()
        for vehicle in env.amrs:
            assert on_edge(vehicle.x, vehicle.y), (
                env.tick_id, vehicle.id, vehicle.estado, vehicle.x, vehicle.y,
                vehicle.posicion_nodo, vehicle.path,
            )
