import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env

class TestRound5_1_BrandMPOriginsAndUniversalRefill(unittest.TestCase):
    """Ronda 5.1: Mapeo de orígenes de insumos por marca y refill en todas las líneas."""

    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    def test_01_peak_nescafe_origin_is_wh_mp_3(self):
        """Pico en Nescafé (L1_OUT) debe crear misión SUPPLY_REQUEST con origen en WH_MP_3."""
        r = self.client.post("/api/v1/sim/peak", json={"line_id": "L1_OUT", "drain_pct": 30.0})
        self.assertEqual(r.status_code, 200)

        # Verificar última misión en cola
        missions = sim_env.mission_queue.get_all_missions()
        latest = next(m for m in missions if m.destino == "L1_OUT" and m.tipo == "SUPPLY_REQUEST")
        self.assertEqual(latest.origen, "WH_MP_3", "Nescafé debe aprovisionarse desde WH_MP_3")

    def test_02_peak_maggi_origin_is_wh_mp_4(self):
        """Pico en Maggi (L2_OUT) debe crear misión SUPPLY_REQUEST con origen en WH_MP_4."""
        r = self.client.post("/api/v1/sim/peak", json={"line_id": "L2_OUT", "drain_pct": 30.0})
        self.assertEqual(r.status_code, 200)

        missions = sim_env.mission_queue.get_all_missions()
        latest = next(m for m in missions if m.destino == "L2_OUT" and m.tipo == "SUPPLY_REQUEST")
        self.assertEqual(latest.origen, "WH_MP_4", "Maggi debe aprovisionarse desde WH_MP_4")

    def test_03_peak_savoy_origin_is_wh_mp_1(self):
        """Pico en Savoy (E1_IN) debe crear misión SUPPLY_REQUEST con origen en WH_MP_1."""
        r = self.client.post("/api/v1/sim/peak", json={"line_id": "E1_IN", "drain_pct": 30.0})
        self.assertEqual(r.status_code, 200)

        missions = sim_env.mission_queue.get_all_missions()
        latest = next(m for m in missions if m.destino == "E1_IN" and m.tipo == "SUPPLY_REQUEST")
        self.assertEqual(latest.origen, "WH_MP_1", "Savoy debe aprovisionarse desde WH_MP_1")

    def test_04_peak_lechera_origin_is_wh_mp_2(self):
        """Pico en La Lechera (E2_IN) debe crear misión SUPPLY_REQUEST con origen en WH_MP_2."""
        r = self.client.post("/api/v1/sim/peak", json={"line_id": "E2_IN", "drain_pct": 30.0})
        self.assertEqual(r.status_code, 200)

        missions = sim_env.mission_queue.get_all_missions()
        latest = next(m for m in missions if m.destino == "E2_IN" and m.tipo == "SUPPLY_REQUEST")
        self.assertEqual(latest.origen, "WH_MP_2", "La Lechera debe aprovisionarse desde WH_MP_2")

    def test_05_guayaquil_nestum_origin_is_wh_mp_5(self):
        """En Guayaquil, pico en Nestum (L3_OUT) debe crear misión SUPPLY_REQUEST desde WH_MP_5."""
        self.client.post("/api/v1/sim/select", json={"plant": "cd_guayaquil"})

        r = self.client.post("/api/v1/sim/peak", json={"line_id": "L3_OUT", "drain_pct": 30.0})
        self.assertEqual(r.status_code, 200)

        missions = sim_env.mission_queue.get_all_missions()
        latest = next(m for m in missions if m.destino == "L3_OUT" and m.tipo == "SUPPLY_REQUEST")
        self.assertEqual(latest.origen, "WH_MP_5", "Nestum en Guayaquil debe aprovisionarse desde WH_MP_5")

    def test_06_universal_refill_all_lines(self):
        """El endpoint de refill debe programar insumos para todas las 4 líneas de Quito."""
        r = self.client.post("/api/v1/sim/refill", json={"target_pct": 90})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("L1_OUT", data["lines"])
        self.assertIn("L2_OUT", data["lines"])
        self.assertIn("E1_IN", data["lines"])
        self.assertIn("E2_IN", data["lines"])

if __name__ == "__main__":
    unittest.main()
