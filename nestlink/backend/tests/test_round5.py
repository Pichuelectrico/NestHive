import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env


class TestRound5_RefillYConsumoBateria(unittest.TestCase):
    """Ronda 5: refill dirigido por objetivo (≥80%) + consumo de batería + autocarga orgánica."""

    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    def test_01_refill_endpoint_sets_target_and_returns_lines(self):
        r = self.client.post("/api/v1/sim/refill", json={"target_pct": 85})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "refill_scheduled")
        self.assertIn("E1_IN", data["lines"])
        self.assertIn("E2_IN", data["lines"])

        line = next(l for l in sim_env.generator.lines if l.id == "E1_IN")
        self.assertAlmostEqual(line.refill_target_pct, 85.0)

        # Línea que no es empacadora / inexistente → 404
        r404 = self.client.post("/api/v1/sim/refill", json={"line_id": "LINEA_INEXISTENTE"})
        self.assertEqual(r404.status_code, 404)

    def test_02_battery_drains_while_moving(self):
        amr = sim_env.amrs[0]
        amr.bateria = 100.0
        amr._move_along_path(dt_sim=1.0, G=sim_env.G)
        # 100 - 0.10*1.0 = 99.90 (consumo proporcional al tiempo en movimiento)
        self.assertAlmostEqual(amr.bateria, 99.90, places=2)

    def test_03_auto_recharge_on_low_battery(self):
        amr = sim_env.amrs[1]
        amr.bateria = 10.0
        amr.estado = "IDLE"
        amr.tarea_actual = None
        sim_env._auto_recharge_check()
        self.assertIsNotNone(amr.tarea_actual)
        self.assertEqual(amr.tarea_actual.tipo, "RECHARGE")
        self.assertGreaterEqual(amr.bateria, 15.0)  # trigger_low_battery fija 15%

    def test_04_refill_chains_supply_until_target(self):
        """Al completar cada entrega se re-encola SUPPLY_REQUEST hasta superar el objetivo."""
        line = next(l for l in sim_env.generator.lines if l.id == "E1_IN")
        line.nivel_pct = 10.0
        initial = sim_env.trigger_refill("E1_IN", target_pct=80.0)
        self.assertEqual(initial, ["E1_IN"])
        total_supplies_generated = 0

        for _ in range(6):
            # Liberar misiones SUPPLY de E1 ya servidas u pendientes para simular entrega
            missions = sim_env.mission_queue.get_all_missions()
            for m in missions:
                if m.tipo == "SUPPLY_REQUEST" and m.destino == "E1_IN":
                    if m.estado in ("pendiente", "asignada", "en_curso"):
                        line.nivel_pct = min(100.0, line.nivel_pct + 65.0)
                        m.estado = "completada"
                        total_supplies_generated += 0  # la contabiliza el paso de generación
            if line.nivel_pct >= 80.0:
                break
            # Avanzar la generación: debería re-encadenar una nueva SUPPLY si aún < objetivo
            sim_env.generator.step(
                dt_sim=1.0,
                mission_queue=sim_env.mission_queue,
                sim_time=sim_env.sim_time,
                metrics_manager=sim_env.metrics,
            )
            new_supplies = sum(
                1 for m in sim_env.mission_queue.get_all_missions()
                if m.tipo == "SUPPLY_REQUEST" and m.destino == "E1_IN"
                and m.estado in ("pendiente", "asignada", "en_curso")
            )
            total_supplies_generated += new_supplies

        self.assertGreaterEqual(line.nivel_pct, 80.0,
                                "El encadenado debe llenar la línea hasta el objetivo ≥80%")
        self.assertGreater(total_supplies_generated, 0,
                           "Deben haberse re-encolado misiones SUPPLY durante el encadenado")


if __name__ == "__main__":
    unittest.main()
