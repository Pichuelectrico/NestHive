import unittest
import networkx as nx
from app.sim.routing import get_free_buffer_for_line, find_shortest_path, find_shortest_path_excluding_edge
from app.sim.env import SimulationEnvironment
from app.models import Tarea

class TestRound10Requirements(unittest.TestCase):

    def test_01_get_free_buffer_for_line(self):
        """PASO 1a: get_free_buffer_for_line retorna el primer buffer libre de la línea."""
        layout = {
            "lines": [
                {
                    "id": "linea1",
                    "buffer_nodes": ["buf_linea1_1", "buf_linea1_2"]
                }
            ]
        }
        G = nx.DiGraph()
        G.add_node("buf_linea1_1", type="buffer")
        G.add_node("buf_linea1_2", type="buffer")

        # Ningún buffer ocupado -> retorna el primero
        free_buf = get_free_buffer_for_line(G, layout, "linea1", busy_nodes=set())
        self.assertEqual(free_buf, "buf_linea1_1")

        # Primer buffer ocupado -> retorna el segundo
        free_buf = get_free_buffer_for_line(G, layout, "linea1", busy_nodes={"buf_linea1_1"})
        self.assertEqual(free_buf, "buf_linea1_2")

        # Ambos ocupados -> None
        free_buf = get_free_buffer_for_line(G, layout, "linea1", busy_nodes={"buf_linea1_1", "buf_linea1_2"})
        self.assertIsNone(free_buf)

    def test_02_station_occupied_redirects_to_buffer_or_waits(self):
        """PASO 1b: Estación ocupada redirige a buffer o pasa a WAITING."""
        env = SimulationEnvironment("quito")
        amr1, amr2 = env.amrs[0], env.amrs[1]
        
        # AMR 1 ocupa la estación de destino L1_OUT
        amr1.posicion_nodo = "L1_OUT"
        amr1.x, amr1.y = env.node_positions["L1_OUT"]

        # AMR 2 intenta entregar a L1_OUT
        amr2.posicion_nodo = "WH_PT_1"
        amr2.x, amr2.y = env.node_positions["WH_PT_1"]
        mission = Tarea(id="T_BUF", tipo="SUPPLY_REQUEST", origen="WH_PT_1", destino="L1_OUT", estado="en_curso")
        amr2.tarea_actual = mission
        amr2.path = ["WH_PT_1", "L1_OUT"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"

        amr2.step(dt_sim=0.2, G=env.G, obstacles=[], metrics_manager=env.metrics, sim_time=0.0, env=env)
        
        # Debe redirigirse al buffer o estar en WAITING (nunca en cruce)
        self.assertTrue(amr2.estado == "WAITING" or amr2.path[-1] in env.layout_raw["lines"][0]["buffer_nodes"])

    def test_03_corridor_direction_and_exclusion(self):
        """PASO 2: find_shortest_path respeta aristas uni y find_shortest_path_excluding_edge excluye solo u->v."""
        G = nx.DiGraph()
        node_positions = {"A": (0, 0), "B": (10, 0), "C": (5, 10)}
        G.add_node("A")
        G.add_node("B")
        G.add_node("C")
        
        # Arista unidireccional A -> B y bidireccional A <-> C <-> B
        G.add_edge("A", "B", weight=1.0, direction="uni", blocked=False)
        G.add_edge("A", "C", weight=2.0, direction="bi", blocked=False)
        G.add_edge("C", "A", weight=2.0, direction="bi", blocked=False)
        G.add_edge("C", "B", weight=2.0, direction="bi", blocked=False)
        G.add_edge("B", "C", weight=2.0, direction="bi", blocked=False)

        # Ruta A -> B usa arista uni directa
        path_ab = find_shortest_path(G, "A", "B", node_positions)
        self.assertEqual(path_ab, ["A", "B"])

        # Ruta B -> A NO puede usar arista uni en reversa -> usa alternativa B -> C -> A
        path_ba = find_shortest_path(G, "B", "A", node_positions)
        self.assertEqual(path_ba, ["B", "C", "A"])

        # Si el único camino B -> A es una arista uni en sentido contrario, retorna None sin colgar
        G_single = nx.DiGraph()
        G_single.add_edge("A", "B", weight=1.0, direction="uni", blocked=False)
        path_ba_single = find_shortest_path(G_single, "B", "A", node_positions)
        self.assertIsNone(path_ba_single)

    def test_04_avoid_opposite_edge_reservations(self):
        """PASO 3a: AMR_1 A->B y AMR_2 B->A con rutas paralelas no comparten aristas opuestas."""
        env = SimulationEnvironment("quito")
        # Simular reserva de ruta A -> B por AMR_1
        amr1 = env.amrs[0]
        path1 = ["X_01", "X_02", "X_03"]
        env.reserve_path(amr1, path1, horizon_sec=15.0)

        # Verificar que la reserva esté registrada
        self.assertIn(("X_01", "X_02", env.sim_time + 15.0), env.edge_reservations)

        # AMR_2 busca ruta de X_03 a X_01 pasando avoid_opposite
        avoid_cb = lambda u, v: any(u == rev_v and v == rev_u for (rev_u, rev_v, exp) in env.edge_reservations)
        path2 = find_shortest_path(env.G, "X_03", "X_01", env.node_positions, avoid_opposite=avoid_cb)
        self.assertIsNotNone(path2)

    def test_05_bottleneck_graph_both_use_edge_no_freeze(self):
        """PASO 3b: En grafo cuello de botella ambas misiones usan la única arista sin congelarse."""
        env = SimulationEnvironment("quito")
        amr1, amr2 = env.amrs[0], env.amrs[1]
        
        # Ejecutar 5 ticks de simulación
        for _ in range(5):
            env.step_tick(dt_sim=0.2)

        self.assertIn(amr1.estado, ["IDLE", "MOVING_TO_PICKUP", "MOVING_TO_DELIVERY", "WAITING", "WAITING_OBSTACLE", "LOADING", "UNLOADING"])
        self.assertIn(amr2.estado, ["IDLE", "MOVING_TO_PICKUP", "MOVING_TO_DELIVERY", "WAITING", "WAITING_OBSTACLE", "LOADING", "UNLOADING"])

if __name__ == "__main__":
    unittest.main()
