import unittest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        # El stack arranca por defecto en "realistic"; esta suite valida endpoints
        # sobre la planta clásica Quito, así que la fijamos explícitamente.
        sim_env.select_plant("quito")
        self.client = TestClient(app)

    def test_01_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")

    def test_02_layout(self):
        response = self.client.get("/api/v1/layout")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("canvas", data)
        self.assertEqual(len(data["nodes"]), 24)

    def test_03_fleet(self):
        response = self.client.get("/api/v1/fleet")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["id"], "AMR_01")

    def test_04_missions(self):
        response = self.client.get("/api/v1/missions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)

    def test_05_block_unblock(self):
        # Block edge X_02 <-> X_05
        block_resp = self.client.post("/api/v1/obstacles/block", json={"from": "X_02", "to": "X_05", "tipo": "SPILL"})
        self.assertEqual(block_resp.status_code, 200)
        self.assertEqual(block_resp.json()["status"], "blocked")

        # Verify edge is blocked in graph
        self.assertTrue(sim_env.G["X_02"]["X_05"]["blocked"])

        # Unblock edge
        unblock_resp = self.client.post("/api/v1/obstacles/unblock", json={"from": "X_02", "to": "X_05"})
        self.assertEqual(unblock_resp.status_code, 200)
        self.assertEqual(unblock_resp.json()["status"], "unblocked")
        self.assertFalse(sim_env.G["X_02"]["X_05"]["blocked"])

    def test_06_sim_peak(self):
        peak_resp = self.client.post("/api/v1/sim/peak", json={"line_id": "E1_IN", "drain_pct": 20.0})
        self.assertEqual(peak_resp.status_code, 200)
        self.assertEqual(peak_resp.json()["status"], "peak_injected")

    def test_07_metrics(self):
        response = self.client.get("/api/v1/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("viajes_completados", data)
        self.assertIn("roi_km_pct", data)

if __name__ == "__main__":
    unittest.main()
