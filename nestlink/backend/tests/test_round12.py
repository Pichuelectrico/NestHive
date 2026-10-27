import unittest
import random
from app.sim.env import SimulationEnvironment
from app.models import Tarea

class TestRound12IdleAMROccupyingNodeFix(unittest.TestCase):
    """Ronda 12: Tests deterministas para arreglar el bug de AMR IDLE estacionado en nodo operativo que bloquea a otros AMRs."""

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

    def test_01_idle_relocation_target_is_non_operational(self):
        """1) Target de reubicación de AMR IDLE en nodo operativo es un hub/cargador no-operativo."""
        amr = self.env.amrs[0]
        amr.posicion_nodo = "WH_MP_1"
        amr.idle_timer = 2.5
        self.env.step_tick(dt_sim=0.2)
        reloc = next((m for m in self.env.mission_queue.missions if m.tipo == "RELOCATION" and m.origen == "WH_MP_1"), None)
        self.assertIsNotNone(reloc)
        target_type = self.env.node_types.get(reloc.destino)
        self.assertNotIn(target_type, ["linea", "empacadora", "almacen"], "Target de relocación no debe ser nodo operativo")

    def test_02_idle_amr_on_operational_node_relocates(self):
        """2) Un AMR que queda IDLE en un nodo operativo (ej. almacén) se reubica tras idle_timer > 2.0s."""
        amr = self.env.amrs[0]
        amr.posicion_nodo = "WH_MP_1"  # Nodo tipo almacén
        amr.x, amr.y = self.env.node_positions["WH_MP_1"]
        amr.estado = "IDLE"
        amr.idle_timer = 2.5

        self.env.step_tick(dt_sim=0.2)

        # Debe haberse encolado una tarea de RELOCATION para mover al AMR
        reloc_missions = [m for m in self.env.mission_queue.missions if m.tipo == "RELOCATION" and m.origen == "WH_MP_1"]
        self.assertGreater(len(reloc_missions), 0, "Debió encolarse una misión de RELOCATION para desalojar el nodo operativo")

    def test_03_incoming_amr_clears_idle_occupant(self):
        """3) AMR en camino hacia un nodo ocupado por un AMR IDLE dispara la reubicación del ocupante."""
        amr1 = self.env.amrs[0] # Ocupante IDLE en WH_MP_1
        amr1.posicion_nodo = "WH_MP_1"
        amr1.x, amr1.y = self.env.node_positions["WH_MP_1"]
        amr1.estado = "IDLE"

        amr2 = self.env.amrs[1] # Entrante
        amr2.posicion_nodo = "X_02"
        amr2.x, amr2.y = self.env.node_positions["X_02"]
        amr2.estado = "MOVING_TO_PICKUP"
        amr2.path = ["X_02", "WH_MP_1"]
        amr2.target_node_idx = 1
        amr2.tarea_actual = Tarea(id="TSK_INCOMING", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="E1_IN", estado="asignada")

        amr2.step(dt_sim=0.2, G=self.env.G, obstacles=[], metrics_manager=self.env.metrics, sim_time=0.0, env=self.env)

        reloc_missions = [m for m in self.env.mission_queue.missions if m.tipo == "RELOCATION" and m.origen == "WH_MP_1"]
        self.assertGreater(len(reloc_missions), 0, "El AMR entrante debió forzar la reubicación del ocupante IDLE")

    def test_04_no_deadlock_between_two_relocating_amrs(self):
        """4) Múltiples AMRs IDLE se reubican a hubs o cargadores libres sin colisionar eternamente."""
        for amr in self.env.amrs:
            amr.posicion_nodo = "WH_MP_1"
            amr.x, amr.y = self.env.node_positions["WH_MP_1"]
            amr.estado = "IDLE"
            amr.idle_timer = 2.5

        # Simular 10 ticks
        for _ in range(10):
            self.env.step_tick(dt_sim=0.2)

        # Los AMRs deben cambiar de estado o haber recibido tareas de reubicación de forma limpia
        states = [a.estado for a in self.env.amrs]
        self.assertTrue(any(s != "IDLE" or a.idle_timer == 0.0 for s, a in zip(states, self.env.amrs)))

if __name__ == "__main__":
    unittest.main()
