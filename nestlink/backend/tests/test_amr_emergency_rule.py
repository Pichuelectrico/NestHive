import json
import random
import unittest
from pathlib import Path
from types import SimpleNamespace

import networkx as nx

from app.data_maps import PLANT_CONFIGS, DEFAULT_PLANT_ID, load_layout_raw
from app.models import Tarea
from app.sim.assignment import compute_hungarian_assignment, default_eligible
from app.sim.env import SimulationEnvironment

POLICY_PATH = Path(__file__).resolve().parents[1] / "app" / "data" / "fleet_policy.json"
POLICY = json.loads(POLICY_PATH.read_text())
WAIT_THRESHOLD_S = float(POLICY["emergency"]["trigger"]["wait_exceeded_seconds"])

# Flota híbrida presentada: 4 AGV + 2 AMR de apoyo (frontend FLEET_PRESENTATION).
# Si la política define "amr_ids", esa es la fuente de verdad.
AMR_IDS = set(POLICY.get("amr_ids", ["AMR_04", "AMR_05"]))


def _vehicle(vid, tipo, x, y, clase):
    return SimpleNamespace(id=vid, tipo=tipo, clase=clase, x=x, y=y, home_zone=None)


def _reco_to_palet(mid="TSK_R1", emergency=False):
    return Tarea(id=mid, tipo="SUPPLY_REQUEST", origen="RECO_R1", destino="PALET_01",
                 prioridad=8, created_at_sim=0.0, emergency=emergency)


def _is_reco_to_palet(m):
    return m.origen.startswith("RECO_") and m.destino.startswith("PALET_")


class TestAmrEmergencyRule(unittest.TestCase):
    """Regla del usuario (New_map.png): los AMR viven en paletizaje→transporte y SOLO
    participan en el abastecimiento R→paletizaje como FALLBACK DE EMERGENCIA.
    El umbral se lee de app/data/fleet_policy.json."""

    def setUp(self):
        random.seed(42)
        self.layout = load_layout_raw("espol_fusion")
        self.pos = {n["id"]: (n["x"], n["y"]) for n in self.layout["nodes"]}
        rx, ry = self.pos["RECO_R1"]
        # El AMR está pegado al origen y el AGV lejos: si la regla no actúa, gana el AMR.
        self.amr = _vehicle("AMR_04", "pallet_lifter", rx, ry, "AMR")
        self.agv = _vehicle("AMR_02", "towing_tug", rx + 300, ry + 200, "AGV")

    def test_00_policy_threshold_is_numeric(self):
        self.assertGreater(WAIT_THRESHOLD_S, 0)

    def test_01_normal_domain_reco_to_palet_goes_to_agv(self):
        """T1: con un AGV disponible, R→paletizaje se asigna al AGV aunque el AMR esté más cerca."""
        assignments = compute_hungarian_assignment([self.amr, self.agv], [_reco_to_palet()], self.pos)
        self.assertEqual(len(assignments), 1)
        self.assertNotIn(assignments[0][0].id, AMR_IDS)

    def test_01b_agv_of_any_hardware_type_takes_reco(self):
        """T1b: la clase (AGV/AMR) decide, no el tipo de hardware. Los AGV de la semilla con
        tipo pallet_lifter/unit_load (AMR_01, AMR_03, AMR_06) deben poder tomar R→paletizaje."""
        rx, ry = self.pos["RECO_R1"]
        for vid, tipo in (("AMR_01", "pallet_lifter"), ("AMR_03", "unit_load"), ("AMR_06", "pallet_lifter")):
            agv = SimpleNamespace(id=vid, tipo=tipo, clase="AGV", x=rx, y=ry, home_zone=None)
            assignments = compute_hungarian_assignment([agv], [_reco_to_palet()], self.pos)
            self.assertEqual(len(assignments), 1, f"{vid} ({tipo}) es AGV y quedó bloqueado")

    def test_02a_only_amr_idle_without_emergency_gets_nothing(self):
        """T2a: sin emergencia, un AMR solo NO toma R→paletizaje (y el asignador no revienta)."""
        assignments = compute_hungarian_assignment([self.amr], [_reco_to_palet()], self.pos)
        self.assertEqual(assignments, [])

    def test_02b_emergency_flag_allows_amr(self):
        """T2b: con la misión marcada emergency=True, el AMR sí puede tomarla."""
        assignments = compute_hungarian_assignment([self.amr], [_reco_to_palet(emergency=True)], self.pos)
        self.assertEqual(len(assignments), 1)
        self.assertIn(assignments[0][0].id, AMR_IDS)

    def test_02c_wait_beyond_threshold_triggers_emergency(self):
        """T2c: una misión R→paletizaje que espera más que el umbral de la política sin AGV
        elegible se marca emergency=True y se avisa con un notice WARN."""
        env = SimulationEnvironment("espol_fusion")
        env.mission_queue.missions = []
        env.notices = []
        for v in env.amrs:
            v.tarea_actual = None
            v.path = []
            v.estado = "CHARGING" if v.id not in AMR_IDS else "IDLE"
        m = env.mission_queue.add_mission("SUPPLY_REQUEST", "RECO_R1", "PALET_01", prioridad=8, sim_time=env.sim_time)
        env.sim_time += WAIT_THRESHOLD_S + 1
        env.step_tick()
        self.assertTrue(m.emergency, "la misión vencida debió marcarse emergency=True")
        self.assertTrue(any(n.tipo == "WARN" for n in env.notices))

    def test_03_after_emergency_amr_does_not_take_regular_reco(self):
        """T3: tras atender una emergencia, una R→paletizaje normal no vuelve a ir al AMR."""
        first = compute_hungarian_assignment([self.amr], [_reco_to_palet("TSK_E", emergency=True)], self.pos)
        self.assertEqual(len(first), 1)
        second = compute_hungarian_assignment([self.amr], [_reco_to_palet("TSK_N")], self.pos)
        self.assertEqual(second, [])

    def test_04_agv_routes_never_cross_transport_edges(self):
        """T4: las aristas paletizaje↔Transporte afuera son dominio AMR: están marcadas en el
        mapa y ninguna ruta de abastecimiento R→paletizaje pasa por TRANSPORTE."""
        transport_edges = [e for e in self.layout["edges"] if "TRANSPORTE" in (e["from"], e["to"])]
        self.assertTrue(transport_edges)
        for e in transport_edges:
            self.assertTrue(e.get("allowed_types"), f"arista {e['from']}->{e['to']} sin dominio")
        env = SimulationEnvironment("espol_fusion")
        palets = sorted(n for n in env.node_positions if n.startswith("PALET_"))
        crossing = [
            (r, p) for r in ("RECO_R1", "RECO_R2", "RECO_R3") for p in palets
            if "TRANSPORTE" in nx.shortest_path(env.G, r, p, weight="weight")
        ]
        self.assertEqual(crossing, [], f"{len(crossing)} rutas R→paletizaje atraviesan TRANSPORTE")

    def test_04b_transport_hub_is_not_a_shortcut(self):
        """T4b (anti-agujero de gusano): entre nodos de la red original de ESPOL ninguna ruta
        más corta atraviesa TRANSPORTE; Transporte afuera no puede ser atajo de la planta."""
        env = SimulationEnvironment("espol_fusion")
        new_prefixes = ("PALET_", "RECO_", "INSUMO_", "FUENTE", "TRANSPORTE")
        base = sorted(n for n in env.node_positions if not n.startswith(new_prefixes))
        crossing = 0
        for src in base:
            _, paths = nx.single_source_dijkstra(env.G, src, weight="weight")
            crossing += sum(1 for dst in base if dst != src and dst in paths and "TRANSPORTE" in paths[dst])
        self.assertEqual(crossing, 0, f"{crossing} rutas entre nodos originales cruzan TRANSPORTE")


class TestFleetClassEligibility(unittest.TestCase):
    """F3-F: la regla híbrida depende de la clase que cada planta asigna a sus vehículos
    (vehículos reales del env, no fixtures)."""

    def _vehicles(self, plant):
        random.seed(42)
        env = SimulationEnvironment(plant)
        return {v.id: v for v in env.amrs}

    def _task(self, tipo):
        return Tarea(id="TSK_X", tipo=tipo, origen="X", destino="Y", prioridad=5)

    def test_08a_realistic_amr04_eligible_supply(self):
        v = self._vehicles("realistic")
        self.assertTrue(default_eligible(v["AMR_04"], self._task("SUPPLY_REQUEST")))

    def test_08b_realistic_amr01_eligible_expedition(self):
        v = self._vehicles("realistic")
        self.assertTrue(default_eligible(v["AMR_01"], self._task("EXPEDITION")))

    def test_08c_espol_export_vehicle_is_an_agv(self):
        env = SimulationEnvironment("espol_fusion")
        self.assertEqual({v.clase for v in env.amrs}, {"AGV"})
        self.assertEqual(env.delivery_amr_ids, {"AMR_04"})

    def test_08d_espol_amr01_not_eligible_expedition(self):
        v = self._vehicles("espol_fusion")
        self.assertEqual(v["AMR_01"].clase, "AGV")
        self.assertFalse(default_eligible(v["AMR_01"], self._task("EXPEDITION")))


class TestAmrEmergencyRunLoop(unittest.TestCase):
    TICKS = 1500  # ≈ 20 min de sim a 0,8 s/tick

    def _run(self):
        random.seed(42)
        env = SimulationEnvironment("espol_fusion")
        last_move = {v.id: (env.sim_time, v.x, v.y) for v in env.amrs}
        max_stuck = 0.0
        for _ in range(self.TICKS):
            env.step_tick()
            for v in env.amrs:
                t0, x0, y0 = last_move[v.id]
                if (v.x, v.y) != (x0, y0) or v.estado in ("IDLE", "CHARGING", "LOADING", "UNLOADING"):
                    last_move[v.id] = (env.sim_time, v.x, v.y)
                else:
                    max_stuck = max(max_stuck, env.sim_time - t0)
        missions = env.mission_queue.get_all_missions()
        emergencies = sum(1 for m in missions if m.emergency)
        done = sum(1 for m in missions if m.estado == "completada")
        reco_pending_age = max(
            [env.sim_time - m.created_at_sim for m in missions
             if _is_reco_to_palet(m) and m.estado == "pendiente"] or [0.0])
        return env, max_stuck, emergencies, done, reco_pending_age

    def test_05_no_starvation_no_stuck(self):
        """T5: con seed 42 ningún vehículo queda inmóvil más que el umbral y ninguna
        R→paletizaje espera más de 2× el umbral."""
        _, max_stuck, _, done, reco_age = self._run()
        self.assertGreater(done, 0)
        self.assertLessEqual(max_stuck, WAIT_THRESHOLD_S)
        self.assertLessEqual(reco_age, 2 * WAIT_THRESHOLD_S)

    def test_06_deterministic_with_seed(self):
        """T6: dos corridas con seed 42 dan el mismo nº de emergencias y misiones completadas."""
        a = self._run()
        b = self._run()
        self.assertEqual((a[2], a[3]), (b[2], b[3]))


def _run_plant(plant, ticks=3000):
    random.seed(42)
    env = SimulationEnvironment(plant)
    agv_on_transport = set()
    for _ in range(ticks):
        env.step_tick()
        for v in env.amrs:
            if v.posicion_nodo == "TRANSPORTE" and v.clase != "AMR":
                agv_on_transport.add(v.id)
    return env, env.mission_queue.get_all_missions(), agv_on_transport


class TestRedChainBehaviour(unittest.TestCase):
    """Cadena roja de espol_fusion (seed 42, 3000 ticks): paletizaje → EXPORT → AMR → TRANSPORTE."""

    @classmethod
    def setUpClass(cls):
        cls.env, cls.missions, cls.agv_on_transport = _run_plant("espol_fusion")
        cls.clase = {v.id: v.clase for v in cls.env.amrs}

    def test_09a_exports_go_palet_to_transport_by_agv(self):
        exports = [m for m in self.missions if m.tipo == "EXPORT" and m.estado == "completada"]
        self.assertGreater(len(exports), 0, "la cadena roja no entregó ningún EXPORT")
        for m in exports:
            self.assertTrue(m.origen.startswith("PALET_"), m.origen)
            self.assertEqual(m.destino, "TRANSPORTE")
            self.assertEqual(self.clase.get(m.amr_asignado), "AGV", f"{m.id} entregado por {m.amr_asignado}")

    def test_09b_only_export_agvs_reach_transport(self):
        exporters = {m.amr_asignado for m in self.missions if m.tipo == "EXPORT"}
        self.assertIn("AMR_04", self.agv_on_transport)
        self.assertTrue(self.agv_on_transport <= exporters)

    def test_09c_chain_is_fed_and_drains(self):
        """Encadenado: hay pallets que llegan a paletizaje (RECO/EXPEDITION) y salen por EXPORT,
        sin EXPORT colgadas más que el umbral de la política."""
        fed = [m for m in self.missions if m.estado == "completada" and m.destino.startswith("PALET_")]
        self.assertGreater(len(fed), 0)
        stale = [m for m in self.missions if m.tipo == "EXPORT" and m.estado != "completada"
                 and self.env.sim_time - m.created_at_sim > 2 * WAIT_THRESHOLD_S]
        self.assertEqual(stale, [])


class TestRealisticOutboundRegression(unittest.TestCase):
    """Guardia de la regresión 18→0: realistic (sin clase en su seed) conserva la salida
    PICKUP_PT → EXPEDITION → OUT → EXPORT al muro (baseline 4cadf58: 19 EXPEDITION / 18 EXPORT)."""

    def test_10_realistic_expedition_and_export_flow(self):
        env, missions, _ = _run_plant("realistic")
        done = [m for m in missions if m.estado == "completada"]
        self.assertGreaterEqual(sum(1 for m in done if m.tipo == "EXPEDITION"), 15)
        self.assertGreaterEqual(sum(1 for m in done if m.tipo == "EXPORT"), 12)
        stale = [m for m in missions if m.tipo in ("EXPEDITION", "EXPORT") and m.estado != "completada"
                 and env.sim_time - m.created_at_sim > 300]
        self.assertEqual(stale, [])


class TestAmrEmergencyRegression(unittest.TestCase):
    def test_07_catalog_and_realistic_untouched(self):
        """T7: el catálogo sigue siendo {espol_fusion, realistic}, default espol_fusion,
        y realistic conserva su geometría (79 nodos)."""
        self.assertEqual(sorted(PLANT_CONFIGS), ["espol_fusion", "realistic"])
        self.assertEqual(DEFAULT_PLANT_ID, "espol_fusion")
        self.assertEqual(len(load_layout_raw("realistic")["nodes"]), 79)


if __name__ == "__main__":
    unittest.main()
