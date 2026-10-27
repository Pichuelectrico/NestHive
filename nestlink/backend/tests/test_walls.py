import unittest
import networkx as nx

from app.data_maps import load_layout_raw, build_plant_graph


def _segments_intersect(p1, p2, p3, p4, tol=1e-9):
    """True si el segmento p1-p2 y el p3-p4 se intersectan (o se tocan)."""

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])

    def on(a, b, c):
        return (
            min(a[0], b[0]) - tol <= c[0] <= max(a[0], b[0]) + tol
            and min(a[1], b[1]) - tol <= c[1] <= max(a[1], b[1]) + tol
        )

    d1, d2 = ccw(p3, p4, p1), ccw(p3, p4, p2)
    d3, d4 = ccw(p1, p2, p3), ccw(p1, p2, p4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    ):
        return True
    if abs(d1) < tol and on(p3, p4, p1):
        return True
    if abs(d2) < tol and on(p3, p4, p2):
        return True
    if abs(d3) < tol and on(p1, p2, p3):
        return True
    if abs(d4) < tol and on(p1, p2, p4):
        return True
    return False


def _wall_crossing_edges(wall, edges, pos):
    """Devuelve las aristas que cruzan el rectángulo del muro 'wall'."""
    rect = [
        (wall["x"], wall["y"]),
        (wall["x"] + wall["w"], wall["y"]),
        (wall["x"] + wall["w"], wall["y"] + wall["h"]),
        (wall["x"], wall["y"] + wall["h"]),
    ]
    hits = []
    for (a, b) in edges:
        ea, eb = pos[a], pos[b]
        for i in range(4):
            if _segments_intersect(
                rect[i], rect[(i + 1) % 4], ea, eb
            ):
                hits.append((a, b))
                break
    return hits


class TestMurallasNoCruzanRutas(unittest.TestCase):
    """Los muros del layout realistic son barreras físicas: ninguna ruta (arista) debe cruzarlos.

    Regla del feedback del usuario: los muros negros NO son transpirables ni por AMRs
    ni por humanos, así que ninguna arista del grafo puede atravesarlos.
    """

    def setUp(self):
        self.layout = load_layout_raw("realistic")
        self.G, self.pos = build_plant_graph(self.layout)
        self.edges = list(self.G.edges())
        self.walls = self.layout.get("walls", [])

    def test_01_muros_requeridos_ausentes_o_vacios(self):
        self.assertGreater(len(self.walls), 0, "El layout realistic debe definir al menos un muro")

    def test_02_ningun_muro_cruza_una_arista(self):
        for wall in self.walls:
            hits = _wall_crossing_edges(wall, self.edges, self.pos)
            self.assertEqual(
                hits,
                [],
                f"Muro {wall.get('id')} ({wall.get('x')},{wall.get('y')} "
                f"{wall.get('w')}x{wall.get('h')}) cruza {len(hits)} arista(s): {hits}",
            )

    def test_03_muros_sin_derivar_en_grafo_desconectado(self):
        self.assertTrue(nx.is_connected(self.G.to_undirected()))
        self.assertEqual(self.G.order(), len(self.layout["nodes"]))


if __name__ == "__main__":
    unittest.main()
