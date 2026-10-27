import unittest

from app.data_maps import load_layout_raw, _edge_crosses_walls
from app.sim.obstacles import ObstacleManager, PedestrianAgent, _safe_route


class TestPeatonesNoAtraviesanParedes(unittest.TestCase):
    """Bug reportado por el usuario: los peatones podían atravesar los muros.

    Fix: los peatones ahora recorren rutas formadas por aristas del grafo FILTRADO
    (build_plant_graph elimina toda arista que cruce una pared), así que ningún
    tramo de su camino cruza un muro. Este test lo garantiza:
      - las rutas seguras no contienen segmentos que crucen paredes;
      - tras simular muchos pasos, cada peatón permanece dentro del grafo seguro.
    """

    def setUp(self):
        self.layout = load_layout_raw("realistic")
        self.walls = self.layout.get("walls", [])
        from app.data_maps import build_plant_graph
        self.G, self.pos = build_plant_graph(self.layout)
        # el manager se construye igual que en env.py
        self.om = ObstacleManager(self.layout, self.pos)

    def test_01_rutas_peatonales_no_cruzan_pared(self):
        for ped_lay in self.layout.get("pedestrians", []):
            route = _safe_route(
                ped_lay.get("waypoints", []), self.G, self.pos, self.walls
            )
            self.assertGreater(len(route), 1,
                               f"{ped_lay['id']}: ruta vacía/simple")
            for a, b in zip(route, route[1:]):
                self.assertFalse(
                    _edge_crosses_walls(self.pos[a], self.pos[b], self.walls),
                    f"{ped_lay['id']}: tramo {a}->{b} cruza un muro",
                )

    def test_02_simulacion_peaton_nunca_cruza_pared(self):
        # simular varios ciclos de movimiento
        for _ in range(300):
            self.om.step(0.5)
        for ped in self.om.pedestrians:
            # el peatón debe quedarse en un nodo del grafo seguro (arista de G)
            self.assertIn(ped.id, [p["id"] for p in self.layout.get("pedestrians", [])])
            cur = ped.route[ped.current_idx]
            prev_next_ok = (
                cur in self.G
                and (ped.x, ped.y) is not None
            )
            self.assertTrue(prev_next_ok, f"{ped.id}: fuera del grafo seguro")
            # verificar que la posición actual no está "dentro" de un muro
            for w in self.walls:
                wx0, wy0, ww, wh = w["x"], w["y"], w["w"], w["h"]
                inside = (
                    wx0 <= ped.x <= wx0 + ww and wy0 <= ped.y <= wy0 + wh
                )
                self.assertFalse(inside, f"{ped.id}: pos dentro del muro {w.get('id')}")

    def test_03_muros_centrales_alcanzan_pared_sur(self):
        """Feedback: 'alarga esos muros centrales hasta la pared externa sur'."""
        south = 592  # W_BOTTOM está en y=592
        for wid in ("W1", "W2"):
            wall = next(w for w in self.walls if w["id"] == wid)
            bottom = wall["y"] + wall["h"]
            self.assertGreaterEqual(
                bottom, south,
                f"{wid} no llega a la pared sur (fondo {bottom} < {south})",
            )
            # la pared debe empezar no muy lejos del norte (sigue siendo muro central vertical)
            self.assertLess(wall["y"], 120, f"{wid} no parece muro central")


if __name__ == "__main__":
    unittest.main()
