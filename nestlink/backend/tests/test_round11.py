import unittest
import random
from app.sim.env import SimulationEnvironment
from app.sim.obstacles import PedestrianAgent
from app.models import Tarea

class TestRound11WaitingForeverBugFix(unittest.TestCase):
    """Ronda 11: Tests deterministas para arreglar el bug de AMRs esperando forever en nodos."""

    def setUp(self):
        random.seed(42)
        self.env = SimulationEnvironment("quito")
        self.env.obstacle_manager.pedestrians = []
        self.env.mission_queue.missions = []
        self.env.notices = []
        for amr in self.env.amrs:
            amr.tarea_actual = None
            amr.path = []
            amr.estado = "IDLE"
            amr.idle_timer = 0.0
            amr.cediendo_paso = False
            amr._estado_desde = self.env.sim_time

    def test_01_waiting_buffer_deadlock_unfreezes_after_timeout(self):
        """1) AMR en estado WAITING (por buffer/estación ocupada) se descongela tras timeout."""
        amr = self.env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = self.env.node_positions["X_02"]
        amr.estado = "WAITING"
        amr._estado_desde = self.env.sim_time - 100.0  # Duración > 90s sim
        amr.tarea_actual = Tarea(id="TSK_WAIT_BUF", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")

        self.env.step_tick(dt_sim=0.2)

        # El timeout debe haber sacado al AMR de WAITING
        self.assertNotEqual(amr.estado, "WAITING", "El AMR en WAITING debió ser descongelado tras >90s")
        self.assertIn(amr.estado, ["MOVING_TO_DELIVERY", "UNLOADING", "IDLE"])

    def test_02_waiting_obstacle_yield_without_winner_unfreezes(self):
        """2) AMR en WAITING_OBSTACLE por cesión de paso sin ganador activo se descongela."""
        amr = self.env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = self.env.node_positions["X_02"]
        amr.estado = "WAITING_OBSTACLE"
        amr.cediendo_paso = True
        amr._estado_desde = self.env.sim_time - 100.0
        amr.tarea_actual = Tarea(id="TSK_YIELD_STUCK", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")

        self.env.step_tick(dt_sim=0.2)

        self.assertNotEqual(amr.estado, "WAITING_OBSTACLE")
        self.assertFalse(amr.cediendo_paso)
        self.assertIn(amr.estado, ["MOVING_TO_DELIVERY", "UNLOADING", "IDLE"])

    def test_03_stationary_pedestrian_does_not_block_forever(self):
        """3) Peatón estacionario (inmóvil) no bloquea al AMR indefinidamente (>90s)."""
        amr = self.env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = self.env.node_positions["X_02"]
        amr.estado = "WAITING_OBSTACLE"
        amr._estado_desde = self.env.sim_time - 100.0
        amr.tarea_actual = Tarea(id="TSK_STAT_PED", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")

        # Peatón inmóvil (speed=0.0) pegado al AMR
        ped = PedestrianAgent(
            id_str="PED_STAT",
            name="Peatón Inmóvil",
            waypoints=["X_02"],
            speed=0.0,
            radius=2.5,
            node_positions=self.env.node_positions
        )
        ped.x, ped.y = amr.x, amr.y
        self.env.obstacle_manager.pedestrians = [ped]

        self.env.step_tick(dt_sim=0.2)

        # Dado que el peatón es inmóvil, el AMR debe ser descongelado automáticamente
        self.assertNotEqual(amr.estado, "WAITING_OBSTACLE", "Peatón estacionario no debe bloquear al AMR indefinidamente")

    def test_04_global_anti_freeze_timeout_recovers_task(self):
        """4) Timeout global restablece ruta o reasigna tarea a la cola si no hay ruta."""
        amr = self.env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = self.env.node_positions["X_02"]
        amr.estado = "WAITING"
        amr._estado_desde = self.env.sim_time - 100.0
        task = Tarea(id="TSK_RECOVER", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")
        amr.tarea_actual = task

        self.env.step_tick(dt_sim=0.2)

        self.assertIn(amr.estado, ["MOVING_TO_DELIVERY", "UNLOADING", "IDLE"])
        unfreeze_notices = [n for n in self.env.notices if "Descongelando" in n.mensaje]
        self.assertGreater(len(unfreeze_notices), 0, "Debió generarse aviso de descongelamiento en notices")

if __name__ == "__main__":
    unittest.main()
