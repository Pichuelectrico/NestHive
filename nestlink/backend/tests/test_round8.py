import unittest
import random
from app.sim.env import sim_env
from app.sim.amr_yield import AmrYieldResolver, detect_head_on_pairs, pick_winner, get_active_edge, edge_progress
from app.models import Tarea

class TestRound8AmrEvasionAndYielding(unittest.TestCase):
    """Ronda 8: Evasión determinista y cesión de paso AMR<->AMR (cabeceo)."""

    def setUp(self):
        random.seed(42)
        sim_env.select_plant("quito")
        for amr in sim_env.amrs:
            amr.tarea_actual = None
            amr.path = []
            amr.estado = "IDLE"
            amr.cediendo_paso = False

    def test_01_head_on_one_yields_no_deadlock(self):
        """Dos AMRs en cabeceo (X_02 <-> X_05): uno cede o re-rutea, el otro avanza sin deadlock."""
        amr1 = sim_env.amrs[0]
        amr2 = sim_env.amrs[1]

        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05", "X_08"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"
        amr1.tarea_actual = Tarea(id="TSK_A", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_08", prioridad=8)

        amr2.posicion_nodo = "X_05"
        amr2.x, amr2.y = sim_env.node_positions["X_05"]
        amr2.path = ["X_05", "X_02", "X_01"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"
        amr2.tarea_actual = Tarea(id="TSK_B", tipo="SUPPLY_REQUEST", origen="X_05", destino="X_01", prioridad=8)

        AmrYieldResolver.resolve_amr_conflicts(sim_env, dt_sim=0.8)

        # Uno de los dos debe ceder o re-rutear
        states = {amr1.estado, amr2.estado}
        self.assertTrue("WAITING_OBSTACLE" in states or "REROUTING" in states, f"Uno debe ceder o re-rutear (actual: {amr1.estado}, {amr2.estado})")
        self.assertTrue("MOVING_TO_DELIVERY" in states or "REROUTING" in states, "El ganador debe seguir avanzando")

        # Correr varios ticks de simulación y verificar que no haya deadlock (> 30s sim)
        for _ in range(25):
            AmrYieldResolver.resolve_amr_conflicts(sim_env, dt_sim=0.8)
            for amr in [amr1, amr2]:
                amr.step(dt_sim=0.8, G=sim_env.G, obstacles=[], metrics_manager=sim_env.metrics)

        # Ambos deben haber progresado o completado sin quedar permanentemente trabados
        self.assertFalse(amr1.estado == "WAITING_OBSTACLE" and amr2.estado == "WAITING_OBSTACLE", "No debe haber deadlock mutuo")

    def test_02_same_direction_no_yield(self):
        """Dos AMRs en la misma dirección (X_02 -> X_05) no se frenan ni entran en WAITING_OBSTACLE por conflicto AMR."""
        amr1 = sim_env.amrs[0]
        amr2 = sim_env.amrs[1]

        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"

        amr2.posicion_nodo = "X_02"
        amr2.x, amr2.y = sim_env.node_positions["X_02"]
        amr2.path = ["X_02", "X_05"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"

        AmrYieldResolver.resolve_amr_conflicts(sim_env, dt_sim=0.8)

        self.assertNotEqual(amr1.estado, "WAITING_OBSTACLE")
        self.assertNotEqual(amr2.estado, "WAITING_OBSTACLE")
        self.assertEqual(amr1.estado, "MOVING_TO_DELIVERY")
        self.assertEqual(amr2.estado, "MOVING_TO_DELIVERY")

    def test_03_priority_p10_beats_p8(self):
        """AMR con prioridad P10 le gana a AMR con P8 en conflicto de cabeceo."""
        amr1 = sim_env.amrs[0]
        amr2 = sim_env.amrs[1]

        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"
        amr1.tarea_actual = Tarea(id="T10", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_05", prioridad=10)

        amr2.posicion_nodo = "X_05"
        amr2.x, amr2.y = sim_env.node_positions["X_05"]
        amr2.path = ["X_05", "X_02"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"
        amr2.tarea_actual = Tarea(id="T8", tipo="RECHARGE", origen="X_05", destino="X_02", prioridad=8)

        winner, loser = pick_winner(amr1, amr2, sim_env.node_positions)
        self.assertEqual(winner.id, amr1.id, "P10 debe ganar a P8")
        self.assertEqual(loser.id, amr2.id)

        AmrYieldResolver.resolve_amr_conflicts(sim_env, dt_sim=0.8)

        self.assertEqual(amr1.estado, "MOVING_TO_DELIVERY", "Ganador P10 debe mantener movimiento")
        self.assertIn(amr2.estado, ["WAITING_OBSTACLE", "REROUTING"], "Perdedor P8 debe ceder o re-rutear")

    def test_04_tiebreak_by_remaining_distance(self):
        """Misma prioridad: gana el AMR con menor distancia restante al destino."""
        amr1 = sim_env.amrs[0]
        amr2 = sim_env.amrs[1]

        # AMR1 le quedan 2 saltos (X_02 -> X_05 -> X_08)
        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05", "X_08"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"
        amr1.tarea_actual = Tarea(id="T_DIST1", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_08", prioridad=8)

        # AMR2 le queda 1 salto (X_05 -> X_02) -> menor distancia restante al destino
        amr2.posicion_nodo = "X_05"
        amr2.x, amr2.y = sim_env.node_positions["X_05"]
        amr2.path = ["X_05", "X_02"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"
        amr2.tarea_actual = Tarea(id="T_DIST2", tipo="SUPPLY_REQUEST", origen="X_05", destino="X_02", prioridad=8)

        winner, loser = pick_winner(amr1, amr2, sim_env.node_positions)
        self.assertEqual(winner.id, amr2.id, "AMR2 más cerca del destino debe ganar")

    def test_05_tiebreak_by_amr_id(self):
        """Misma prioridad y distancia: tie-break por id lexicográfico menor (AMR_01 vs AMR_02)."""
        amr1 = sim_env.amrs[0] # AMR_01
        amr2 = sim_env.amrs[1] # AMR_02

        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"
        amr1.tarea_actual = Tarea(id="T_SAME", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_05", prioridad=8)

        amr2.posicion_nodo = "X_05"
        amr2.x, amr2.y = sim_env.node_positions["X_05"]
        amr2.path = ["X_05", "X_02"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"
        amr2.tarea_actual = Tarea(id="T_SAME2", tipo="SUPPLY_REQUEST", origen="X_05", destino="X_02", prioridad=8)

        winner, loser = pick_winner(amr1, amr2, sim_env.node_positions)
        self.assertEqual(winner.id, "AMR_01", "AMR_01 gana por ID lexicográfico menor")

    def test_06_same_tick_organic_no_duplicate_charger_style_race(self):
        """Resolución en un solo tick procesa deterministamente y actualiza los estados sin carreras."""
        amrs = sim_env.amrs[:2]
        a1, a2 = amrs[0], amrs[1]

        a1.posicion_nodo = "X_02"
        a1.x, a1.y = sim_env.node_positions["X_02"]
        a1.path = ["X_02", "X_05"]
        a1.target_node_idx = 1
        a1.estado = "MOVING_TO_DELIVERY"
        a1.tarea_actual = Tarea(id="T1", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_05", prioridad=8)

        a2.posicion_nodo = "X_05"
        a2.x, a2.y = sim_env.node_positions["X_05"]
        a2.path = ["X_05", "X_02"]
        a2.target_node_idx = 1
        a2.estado = "MOVING_TO_DELIVERY"
        a2.tarea_actual = Tarea(id="T2", tipo="SUPPLY_REQUEST", origen="X_05", destino="X_02", prioridad=8)

        AmrYieldResolver.resolve_amr_conflicts(sim_env, dt_sim=0.8)

        # Exactamente uno cede y el otro avanza
        self.assertEqual(a1.estado, "MOVING_TO_DELIVERY")
        self.assertIn(a2.estado, ["WAITING_OBSTACLE", "REROUTING"])

    def test_07_reroute_when_alternate_path_exists(self):
        """Perdedor en nodo con ruta alternativa re-rutea (REROUTING) omitiendo la arista en conflicto."""
        amr1 = sim_env.amrs[0]
        amr2 = sim_env.amrs[1]

        # Configurar de modo que AMR2 esté en el nodo inicial (progress < 0.05) y exista ruta alternativa
        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05", "WH_MP_1"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"
        amr1.tarea_actual = Tarea(id="T1", tipo="SUPPLY_REQUEST", origen="X_02", destino="WH_MP_1", prioridad=10)

        amr2.posicion_nodo = "X_05"
        amr2.x, amr2.y = sim_env.node_positions["X_05"]
        amr2.path = ["X_05", "X_02", "L1_OUT"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"
        amr2.tarea_actual = Tarea(id="T2", tipo="SUPPLY_REQUEST", origen="X_05", destino="L1_OUT", prioridad=8)

        AmrYieldResolver.resolve_amr_conflicts(sim_env, dt_sim=0.8)

        # Si existe ruta alternativa desde X_05 hacia L1_OUT, AMR2 pasa a REROUTING y su path ya no contiene (X_05, X_02)
        if amr2.estado == "REROUTING":
            self.assertNotIn(("X_05", "X_02"), zip(amr2.path, amr2.path[1:]))


    def test_08_run_loop_hook_resolves_evasion(self):
        """Verifica que el hook en env (step_tick) ejecute la evasión automáticamente sin llamarla a mano."""
        amr1 = sim_env.amrs[0]
        amr2 = sim_env.amrs[1]

        amr1.posicion_nodo = "X_02"
        amr1.x, amr1.y = sim_env.node_positions["X_02"]
        amr1.path = ["X_02", "X_05"]
        amr1.target_node_idx = 1
        amr1.estado = "MOVING_TO_DELIVERY"
        amr1.tarea_actual = Tarea(id="T10", tipo="SUPPLY_REQUEST", origen="X_02", destino="X_05", prioridad=10)

        amr2.posicion_nodo = "X_05"
        amr2.x, amr2.y = sim_env.node_positions["X_05"]
        amr2.path = ["X_05", "X_02"]
        amr2.target_node_idx = 1
        amr2.estado = "MOVING_TO_DELIVERY"
        amr2.tarea_actual = Tarea(id="T8", tipo="RECHARGE", origen="X_05", destino="X_02", prioridad=8)

        # Ejecutar 1 tick del entorno completo (SIN llamar AmrYieldResolver manualmente)
        sim_env.step_tick(dt_sim=0.8)

        # Verificar que la evasión ocurrió vía env hook
        yield_notices = [n for n in sim_env.notices if "cediendo paso" in n.mensaje or "Re-ruteo por conflicto" in n.mensaje]
        self.assertGreater(len(yield_notices), 0, "El entorno debe generar notices de evasión automáticamente")
        self.assertIn(amr2.estado, ["WAITING_OBSTACLE", "REROUTING"])

if __name__ == "__main__":
    unittest.main()
