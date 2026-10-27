import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env
from app.models import Tarea

class TestRound4Features(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    def test_01_packing_line_restock_on_supply_delivery(self):
        """Verifica que el restock aumente el nivel_pct de empacadoras al entregar SUPPLY_REQUEST."""
        # 1. Simular nivel bajo en E1_IN (15%)
        line = next(l for l in sim_env.generator.lines if l.id == "E1_IN")
        line.nivel_pct = 15.0
        initial_lvl = line.nivel_pct

        # 2. Asignar y completar una misión SUPPLY_REQUEST en E1_IN
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "E1_IN"
        amr.x, amr.y = sim_env.node_positions["E1_IN"]
        amr.estado = "UNLOADING"
        amr.loading_timer = 0.05
        amr.tarea_actual = Tarea(
            id="TSK_TEST_SUPPLY",
            tipo="SUPPLY_REQUEST",
            origen="WH_MP_1",
            destino="E1_IN",
            prioridad=10,
            estado="en_curso"
        )

        # 3. Avanzar step para completar UNLOADING
        amr.step(
            dt_sim=0.1,
            G=sim_env.G,
            obstacles=[],
            metrics_manager=sim_env.metrics,
            generator_manager=sim_env.generator,
            sim_time=50.0
        )

        # 4. Verificar que la línea recibió restock (+65%) y subió de nivel
        self.assertGreater(line.nivel_pct, initial_lvl)
        self.assertEqual(line.nivel_pct, 35.0) # 15 + 20 = 35%

    def test_02_charging_only_allowed_in_carga_nodes(self):
        """Verifica que el estado CHARGING sea rechazado si el nodo no es tipo carga."""
        amr = sim_env.amrs[1]
        amr.posicion_nodo = "X_02" # Nodo tipo 'cruce'
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.estado = "CHARGING" # Forzar estado erróneo

        # Step debe detectar que X_02 no es 'carga' y cambiar a MOVING_TO_DELIVERY hacia cargador
        amr.step(
            dt_sim=0.1,
            G=sim_env.G,
            obstacles=[],
            metrics_manager=sim_env.metrics,
            generator_manager=sim_env.generator,
            sim_time=50.0
        )

        self.assertNotEqual(amr.estado, "CHARGING", "No debe permitir CHARGING fuera de estaciones de carga")
        self.assertEqual(amr.estado, "MOVING_TO_DELIVERY")
        self.assertIn(amr.path[-1], ["CHARGER_1", "CHARGER_2"])

        # Ahora ubicarlo en CHARGER_1 y verificar que sí cargue
        amr.posicion_nodo = "CHARGER_1"
        amr.x, amr.y = sim_env.node_positions["CHARGER_1"]
        amr.estado = "CHARGING"
        amr.bateria = 30
        amr.step(
            dt_sim=1.0,
            G=sim_env.G,
            obstacles=[],
            metrics_manager=sim_env.metrics,
            generator_manager=sim_env.generator,
            sim_time=60.0
        )
        self.assertEqual(amr.estado, "CHARGING")
        self.assertGreater(amr.bateria, 30)

    def test_03_mission_assignment_integrity_no_hanging_tasks(self):
        """Verifica que si no hay ruta para una misión, no se cuelgue al AMR ni a la tarea."""
        # Desconectar temporalmente un nodo ficticio o inalcanzable
        mission = Tarea(
            id="TSK_UNREACHABLE",
            tipo="SUPPLY_REQUEST",
            origen="NODO_INEXISTENTE",
            destino="E1_IN",
            prioridad=10,
            estado="pendiente"
        )
        amr = sim_env.amrs[2]
        amr.estado = "IDLE"
        amr.tarea_actual = None

        success = amr.assign_mission(mission, sim_env.G)
        self.assertFalse(success, "assign_mission debe retornar False si el nodo es inalcanzable")
        self.assertEqual(amr.estado, "IDLE")
        self.assertIsNone(amr.tarea_actual)

if __name__ == "__main__":
    unittest.main()
