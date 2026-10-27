import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env

class TestRound6OccupancyAwareChargerSelection(unittest.TestCase):
    """Ronda 6: Selección inteligente de cargadores considerando ocupación real y costo métrico."""

    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    def test_01_two_amrs_distributed_to_different_chargers(self):
        """Verifica que dos AMRs sucesivos con batería baja se distribuyan a cargadores distintos."""
        # 1. Batería baja para AMR_01
        r1 = self.client.post("/api/v1/sim/low_battery", json={"amr_id": "AMR_01"})
        self.assertEqual(r1.status_code, 200)
        target1 = r1.json()["target"]

        # 2. Batería baja para AMR_02
        r2 = self.client.post("/api/v1/sim/low_battery", json={"amr_id": "AMR_02"})
        self.assertEqual(r2.status_code, 200)
        target2 = r2.json()["target"]

        # Deben ser cargadores diferentes
        self.assertNotEqual(target1, target2, f"Los dos AMRs no deben ir al mismo cargador ({target1} vs {target2})")
        self.assertTrue({target1, target2}.issubset({"CHARGER_1", "CHARGER_2"}))

    def test_02_occupied_charger_forces_selection_of_free_charger(self):
        """Verifica que si CHARGER_1 está ocupado, el siguiente AMR elija CHARGER_2."""
        # Forzar AMR_03 en CHARGING en CHARGER_1
        amr3 = next(a for a in sim_env.amrs if a.id == "AMR_03")
        amr3.posicion_nodo = "CHARGER_1"
        amr3.estado = "CHARGING"
        amr3.bateria = 20

        # Disparar low battery en AMR_04
        best = sim_env.find_best_charger("AMR_04")
        self.assertEqual(best, "CHARGER_2", "Debe elegir el cargador libre CHARGER_2")

    def test_03_least_occupied_selected_when_all_chargers_busy(self):
        """Si ambos cargadores tienen AMRs, elige el de menor carga o menor costo."""
        amr1 = next(a for a in sim_env.amrs if a.id == "AMR_01")
        amr2 = next(a for a in sim_env.amrs if a.id == "AMR_02")
        amr3 = next(a for a in sim_env.amrs if a.id == "AMR_03")

        amr1.posicion_nodo = "CHARGER_1"
        amr1.estado = "CHARGING"

        amr2.posicion_nodo = "CHARGER_1"
        amr2.estado = "CHARGING"

        amr3.posicion_nodo = "CHARGER_2"
        amr3.estado = "CHARGING"

        # AMR_04 debe elegir CHARGER_2 (ocupación 1 vs 2)
        best = sim_env.find_best_charger("AMR_04")
        self.assertEqual(best, "CHARGER_2")

    def test_04_agents_uses_resolver_and_never_charges_outside_carga_node(self):
        """Verifica que el agente use el charger_resolver y rechace CHARGING fuera de un nodo tipo carga."""
        amr = sim_env.amrs[0]
        self.assertIsNotNone(amr.charger_resolver)
        amr.posicion_nodo = "X_05" # Cruce
        amr.estado = "CHARGING"

        amr.step(
            dt_sim=0.1,
            G=sim_env.G,
            obstacles=[],
            metrics_manager=sim_env.metrics,
            sim_time=100.0,
            generator_manager=sim_env.generator
        )

        self.assertNotEqual(amr.estado, "CHARGING")
        self.assertEqual(amr.estado, "MOVING_TO_DELIVERY")
        self.assertTrue(any(ch in amr.path[-1] for ch in ["CHARGER_1", "CHARGER_2"]))

    def test_05_recharge_path_fallback_uses_mission_destino_not_charger_0(self):
        """Si RECHARGE termina fuera de nodo carga, re-rutear al destino de la misión (no chargers[0])."""
        from app.models import Tarea

        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_05"
        amr.x, amr.y = sim_env.node_positions["X_05"]
        amr.estado = "MOVING_TO_DELIVERY"
        amr.path = ["X_05"]
        amr.target_node_idx = 1
        amr.tarea_actual = Tarea(
            id="TSK_R_TEST",
            tipo="RECHARGE",
            origen="X_05",
            destino="CHARGER_2",
            prioridad=8,
            estado="en_curso",
            amr_asignado=amr.id,
            peso_kg=0.0,
            created_at_sim=0.0,
        )

        amr._move_along_path(0.1, sim_env.G)

        self.assertEqual(amr.estado, "MOVING_TO_DELIVERY")
        self.assertTrue(amr.path, "Debe calcular nueva ruta hacia el cargador")
        self.assertEqual(amr.path[-1], "CHARGER_2", "Fallback debe usar destino RECHARGE, no CHARGER_1")

    def test_06_auto_recharge_same_tick_distributes_chargers(self):
        """Dos AMRs con batería ≤15% en el mismo tick orgánico → cargadores distintos."""
        for amr in sim_env.amrs:
            amr.bateria = 100.0
            amr.estado = "IDLE"
            amr.tarea_actual = None
            amr.path = []

        amr1 = next(a for a in sim_env.amrs if a.id == "AMR_01")
        amr2 = next(a for a in sim_env.amrs if a.id == "AMR_02")
        amr1.bateria = 14.0
        amr2.bateria = 14.0

        sim_env._auto_recharge_check()

        targets = []
        for amr in (amr1, amr2):
            self.assertIsNotNone(amr.tarea_actual)
            self.assertEqual(amr.tarea_actual.tipo, "RECHARGE")
            targets.append(amr.tarea_actual.destino)

        self.assertNotEqual(
            targets[0],
            targets[1],
            f"En el mismo tick orgánico deben ir a cargadores distintos: {targets}",
        )

if __name__ == "__main__":
    unittest.main()
