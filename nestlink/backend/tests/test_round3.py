import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env

class TestRound3LowBattery(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    def test_01_low_battery_success(self):
        """Verifica que POST /sim/low_battery ponga la batería en 15% y cree misión RECHARGE."""
        resp = self.client.post("/api/v1/sim/low_battery", json={"amr_id": "AMR_01"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["amr_id"], "AMR_01")
        self.assertIn(data["target"], ["CHARGER_1", "CHARGER_2"])

        # Verificar estado del AMR
        amr = next(a for a in sim_env.amrs if a.id == "AMR_01")
        self.assertEqual(amr.bateria, 15)
        self.assertIsNotNone(amr.tarea_actual)
        self.assertEqual(amr.tarea_actual.tipo, "RECHARGE")
        self.assertEqual(amr.tarea_actual.prioridad, 8)
        self.assertEqual(amr.tarea_actual.destino, data["target"])

        # Verificar que la misión aparece en /api/v1/missions
        resp_missions = self.client.get("/api/v1/missions")
        self.assertEqual(resp_missions.status_code, 200)
        missions = resp_missions.json()
        recharge_missions = [m for m in missions if m["tipo"] == "RECHARGE" and m["amr_asignado"] == "AMR_01"]
        self.assertEqual(len(recharge_missions), 1)

    def test_02_low_battery_charging_and_recovery(self):
        """Verifica que al llegar al cargador el AMR entre a CHARGING y recupere su batería a 100%."""
        self.client.post("/api/v1/sim/low_battery", json={"amr_id": "AMR_02"})
        amr = next(a for a in sim_env.amrs if a.id == "AMR_02")
        self.assertEqual(amr.bateria, 15)

        # Forzar AMR a posición de cargador
        target_charger = amr.tarea_actual.destino
        amr.posicion_nodo = target_charger
        amr.x, amr.y = sim_env.node_positions[target_charger]
        amr.estado = "CHARGING"
        amr.path = []

        # Simular avance de tiempo para recarga
        initial_bat = amr.bateria
        amr.step(
            dt_sim=5.0,
            G=sim_env.G,
            obstacles=[],
            metrics_manager=sim_env.metrics,
            sim_time=100.0
        )
        self.assertGreater(amr.bateria, initial_bat)

        # Simular recarga completa (25s adicionales)
        for _ in range(5):
            amr.step(
                dt_sim=5.0,
                G=sim_env.G,
                obstacles=[],
                metrics_manager=sim_env.metrics,
                sim_time=120.0
            )

        self.assertEqual(amr.bateria, 100)
        self.assertEqual(amr.estado, "IDLE")
        self.assertIsNone(amr.tarea_actual)

    def test_03_low_battery_not_found(self):
        """Verifica que un amr_id inexistente devuelva 404."""
        resp = self.client.post("/api/v1/sim/low_battery", json={"amr_id": "AMR_INEXISTENTE"})
        self.assertEqual(resp.status_code, 404)
        self.assertIn("no encontrado", resp.json()["detail"])

if __name__ == "__main__":
    unittest.main()
