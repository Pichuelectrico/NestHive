# tests/test_smoke.py
# Smoke tests para validar carga de datos, grafo, ruteo A* con bloqueos y asignación

import unittest
import networkx as nx
from app.data_maps import load_layout_raw, load_seeds_raw, build_plant_graph
from app.sim.routing import find_shortest_path, block_edge, unblock_edge
from app.sim.assignment import MissionQueue, compute_hungarian_assignment
from app.sim.agents import AMRAgent

class TestNestLinkSmoke(unittest.TestCase):

    def setUp(self):
        # Smoke tests del grafo canónico Quito (24 nodos). El stack arranca por
        # defecto en "realistic" (75 nodos), así que fijamos la planta explícitamente.
        self.layout_raw = load_layout_raw("quito")
        self.seeds_raw = load_seeds_raw("quito")
        self.G, self.node_positions = build_plant_graph(self.layout_raw)

    def test_01_graph_connected(self):
        """Verifica que el grafo de la planta sea conexo y tenga los 22 nodos canónicos."""
        self.assertEqual(self.G.number_of_nodes(), 24)
        # Convertir a no dirigido para chequear conexidad general
        undirected_G = self.G.to_undirected()
        self.assertTrue(nx.is_connected(undirected_G), "El grafo de la planta debe ser conexo.")

    def test_02_astar_routing(self):
        """Verifica que A* encuentre una ruta válida entre L1_OUT y WH_PT_1."""
        path = find_shortest_path(self.G, "L1_OUT", "WH_PT_1", self.node_positions)
        self.assertIsNotNone(path)
        self.assertEqual(path[0], "L1_OUT")
        self.assertEqual(path[-1], "WH_PT_1")
        self.assertIn("X_01", path)

    def test_03_astar_rerouting_on_block(self):
        """Verifica que al bloquear X_01 <-> X_02, A* encuentre una ruta alternativa."""
        # Ruta original
        path_before = find_shortest_path(self.G, "L1_OUT", "WH_PT_1", self.node_positions)
        self.assertIn("X_02", path_before)

        # Bloquear arista X_01 <-> X_02
        block_edge(self.G, "X_01", "X_02")

        # Nueva ruta
        path_after = find_shortest_path(self.G, "L1_OUT", "WH_PT_1", self.node_positions)
        self.assertIsNotNone(path_after)
        self.assertNotIn("X_02", path_after[1:3], "La ruta debe evitar la arista bloqueada X_01-X_02")

        # Desbloquear
        unblock_edge(self.G, "X_01", "X_02")
        path_restored = find_shortest_path(self.G, "L1_OUT", "WH_PT_1", self.node_positions)
        self.assertIn("X_02", path_restored)

    def test_04_hungarian_assignment(self):
        """Verifica que el método Húngaro asigne correctamente tareas a AMRs libres."""
        mq = MissionQueue()
        m1 = mq.add_mission("SUPPLY_REQUEST", "WH_MP_1", "E1_IN", prioridad=10)
        m2 = mq.add_mission("PICKUP_PT", "L1_OUT", "WH_PT_1", prioridad=5)

        amr1 = AMRAgent("AMR_01", "Nescafé Shuttle", posicion_nodo="WH_MP_1", node_positions=self.node_positions)
        amr2 = AMRAgent("AMR_02", "Savoy Express", posicion_nodo="L1_OUT", node_positions=self.node_positions)

        assignments = compute_hungarian_assignment([amr1, amr2], mq.get_pending_missions(), self.node_positions)
        self.assertEqual(len(assignments), 2)
        # AMR1 está en WH_MP_1 por lo que debe recibir m1 (origen WH_MP_1)
        self.assertEqual(assignments[0][0].id, "AMR_01")
        self.assertEqual(assignments[0][1].id, m1.id)

if __name__ == "__main__":
    unittest.main()
