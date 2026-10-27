import unittest
import random
from app.sim.env import sim_env
from app.sim.routing import block_edge, unblock_edge
from app.sim.obstacles import PedestrianAgent
from app.models import Tarea

class TestRound9ReroutingHotfixAndFreezeTimeout(unittest.TestCase):
    """Ronda 8.3/8.4: Despacho de REROUTING, desvío correcto y timeout anti-congelamiento (90s)."""

    def setUp(self):
        random.seed(42)
        sim_env.select_plant("quito")
        sim_env.obstacle_manager.pedestrians = []
        sim_env.mission_queue.missions = []
        sim_env.notices = []
        for line in sim_env.generator.lines:
            line.nivel_pct = 100.0
        for amr in sim_env.amrs:
            amr.tarea_actual = None
            amr.path = []
            amr.estado = "IDLE"
            amr.idle_timer = 0.0
            amr.cediendo_paso = False
            amr._estado_desde = sim_env.sim_time

    def test_01_step_dispatch_rerouting_resumes(self):
        """AMR en estado REROUTING con path válido reanuda movimiento al llamar amr.step()."""
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.path = ["X_02", "X_05", "X_08"]
        amr.target_node_idx = 1
        amr.estado = "REROUTING"
        amr.tarea_actual = Tarea(id="TSK_REROUTE", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_08", estado="en_curso")

        initial_x, initial_y = amr.x, amr.y

        # Ejecutar 1 paso de cinemática
        amr.step(dt_sim=0.8, G=sim_env.G, obstacles=[], metrics_manager=sim_env.metrics, sim_time=sim_env.sim_time)

        # El estado debe cambiar a MOVING_TO_DELIVERY y la posición debe cambiar (avanzar)
        self.assertIn(amr.estado, ["MOVING_TO_DELIVERY", "MOVING_TO_PICKUP"])
        self.assertTrue(amr.x != initial_x or amr.y != initial_y, "El AMR en REROUTING debió avanzar físicamente")

    def test_02_reroute_uses_correct_dest_for_delivery(self):
        """AMR en MOVING_TO_DELIVERY al encontrar arista bloqueada re-rutea a .destino y no a .origen."""
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.path = ["X_02", "X_05", "X_08"]
        amr.target_node_idx = 1
        amr.estado = "MOVING_TO_DELIVERY"
        amr.tarea_actual = Tarea(id="TSK_DELIVERY", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")

        # Bloquear el tramo X_02 -> X_05
        block_edge(sim_env.G, "X_02", "X_05")
        try:
            amr.step(dt_sim=0.8, G=sim_env.G, obstacles=[], metrics_manager=sim_env.metrics, sim_time=sim_env.sim_time)
            
            # La última parada del nuevo path debe ser el destino X_08 (NO el origen WH_MP_1)
            self.assertEqual(amr.path[-1], "X_08", f"El re-ruteo debió dirigirse al destino X_08, pero fue a {amr.path[-1]}")
        finally:
            unblock_edge(sim_env.G, "X_02", "X_05")

    def test_03_unfreeze_after_90s_REROUTING(self):
        """Un AMR petrificado en REROUTING por >= 90s sim se descongela automáticamente vía timeout en env."""
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.path = ["X_02"]
        amr.target_node_idx = 1
        amr.estado = "REROUTING"
        amr._estado_desde = sim_env.sim_time - 100.0  # Forzar duracion > 90s sim
        amr.tarea_actual = Tarea(id="TSK_STUCK", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")

        sim_env.step_tick(dt_sim=0.8)

        self.assertNotEqual(amr.estado, "REROUTING", "El timeout de 90s debió cambiar el estado")
        self.assertIn(amr.estado, ["MOVING_TO_DELIVERY", "IDLE"])

        unfreeze_notices = [n for n in sim_env.notices if "Descongelando" in n.mensaje]
        self.assertGreater(len(unfreeze_notices), 0, "Debió emitirse aviso de descongelamiento en notices")

    def test_04_no_freeze_when_path_resolves_quickly(self):
        """Un AMR en REROUTING con path válido no espera 30s; reanuda inmediatamente."""
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.path = ["X_02", "X_03", "WH_PT_1"]
        amr.target_node_idx = 1
        amr.estado = "REROUTING"
        amr._estado_desde = sim_env.sim_time - 2.0  # Solo 2s en REROUTING
        amr.tarea_actual = Tarea(id="TSK_FAST", tipo="SUPPLY_REQUEST", origen="X_02", destino="WH_PT_1", estado="en_curso")

        sim_env.step_tick(dt_sim=0.8)

        # Reanuda inmediatamente a MOVING_TO_DELIVERY
        self.assertEqual(amr.estado, "MOVING_TO_DELIVERY")

    def test_05_timeout_no_forced_on_pedestrian_wait(self):
        """AMR en WAITING_OBSTACLE con peatón dentro del radio NO se descongela tras >90s sim."""
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.path = ["X_02", "X_05", "X_08"]
        amr.target_node_idx = 1
        amr.estado = "WAITING_OBSTACLE"
        amr._estado_desde = sim_env.sim_time - 100.0
        amr.tarea_actual = Tarea(id="TSK_PED_WAIT", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")

        ped = PedestrianAgent(
            id_str="PED_TEST",
            name="Operario Test",
            waypoints=["X_02", "X_05"],
            speed=0.0,
            radius=2.5,
            node_positions=sim_env.node_positions,
        )
        ped.x, ped.y = amr.x, amr.y
        sim_env.obstacle_manager.pedestrians = [ped]

        sim_env.step_tick(dt_sim=0.8)

        self.assertEqual(amr.estado, "WAITING_OBSTACLE", "No debe forzar descongelamiento con peatón activo cerca")
        unfreeze_notices = [n for n in sim_env.notices if "Descongelando" in n.mensaje]
        self.assertEqual(len(unfreeze_notices), 0, "No debe emitir aviso de descongelamiento por espera legítima a peatón")

    def test_06_timeout_90s_rerouting_no_obstacle(self):
        """AMR en REROUTING sin peatón y >90s sim se descongela (MOVING o IDLE)."""
        amr = sim_env.amrs[0]
        amr.posicion_nodo = "X_02"
        amr.x, amr.y = sim_env.node_positions["X_02"]
        amr.path = ["X_02"]
        amr.target_node_idx = 1
        amr.estado = "REROUTING"
        amr._estado_desde = sim_env.sim_time - 100.0
        amr.tarea_actual = Tarea(id="TSK_REROUTE_STUCK", tipo="SUPPLY_REQUEST", origen="WH_MP_1", destino="X_08", estado="en_curso")
        sim_env.obstacle_manager.pedestrians = []

        sim_env.step_tick(dt_sim=0.8)

        self.assertNotEqual(amr.estado, "REROUTING")
        self.assertIn(amr.estado, ["MOVING_TO_DELIVERY", "IDLE"])

if __name__ == "__main__":
    unittest.main()
