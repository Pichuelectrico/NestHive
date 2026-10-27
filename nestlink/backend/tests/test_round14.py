import unittest
import random
from app.sim.env import SimulationEnvironment
from app.models import Tarea

class TestRound14RechargeBuyKPIOutWait(unittest.TestCase):
    """Ronda 2.8:
    - BUG: el AMR exclusivo de entrega (AMR_06) fue a cargar y un EXPORT en vuelo que traía un
      paquete hacia el muro quedó 'olvidado' (out_en_ruta sin liberar) → el paquete ocupaba el
      OUT para siempre. Fix: abort_export revierte el estado del OUT y reprograma la entrega.
    - KPI nuevo: tiempo medio de paquetes en OUTs previo a la entrega al muro (arribo → ship)."""

    def setUp(self):
        random.seed(42)
        self.env = SimulationEnvironment("realistic")
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

    def _amr6(self):
        return next(a for a in self.env.amrs if a.id == "AMR_06")

    def _pend_exp(self, origin="OUT"):
        return [
            m for m in self.env.mission_queue.get_all_missions()
            if m.tipo == "EXPORT" and origin and m.origen == origin
            and m.estado in ("pendiente", "asignada")
        ]

    def test_01_export_en_vuelo_abortada_por_recarga_no_queda_out_atrapado(self):
        """BUG: un EXPORT en vuelo (AMR_06 con paquete rumbo al muro) se interrumpe porque la
        batería cae ≤15% y el AMR prioriza recargar. Tras volver (batería llena), el paquete NO
        puede quedar 'olvidado': el OUT debe quedar con stock y EXPORT reprogramada, y AMR_06 lo
        entrega → OUT drena a 0, sin paquete ocupándolo eternamente."""
        env = self.env
        # (a) llega un paquete a OUT → EXPORT provisionada y asignada al AMR exclusivo (en vuelo)
        env.out_arrive("OUT", 100.0)
        self.assertEqual(env.out_stock["OUT"], 1)
        self.assertEqual(env.out_en_ruta["OUT"], 1)
        amr6 = self._amr6()
        amr6.posicion_nodo = "MURO_ENTREGA"
        amr6.x, amr6.y = env.node_positions["MURO_ENTREGA"]
        amr6.estado = "IDLE"
        amr6.idle_timer = 1.0
        env._dispatch_exports()
        self.assertEqual(amr6.tarea_actual.tipo, "EXPORT")
        self.assertEqual(amr6.tarea_actual.origen, "OUT")
        amr6.estado = "MOVING_TO_PICKUP"  # en vuelo hacia el OUT con el EXPORT cargado

        # (b) batería cae a 15% mientras el EXPORT va en vuelo → recarga prioritaria: interrumpe
        amr6.bateria = 12.0
        env._auto_recharge_check()
        self.assertEqual(amr6.tarea_actual.tipo, "RECHARGE",
                         "La recarga interrumpe el EXPORT en vuelo")
        # FIX (antes del fix esto fallaba): el slot ya se liberó y la EXPORT se reprogramó
        self.assertEqual(env.out_en_ruta["OUT"], 1, "Slot liberado y EXPORT reprogramada (no 0 colgado)")
        self.assertEqual(env.out_stock["OUT"], 1, "El paquete NO se pierde: sigue en el buffer del OUT")
        self.assertEqual(len(self._pend_exp("OUT")), 1, "Queda un EXPORT pendiente para el OUT")
        self.assertFalse(
            any(m.tipo == "EXPORT" and m.origen == "OUT" and m.estado == "en_curso" and m.id != amr6.tarea_actual.id
                for m in env.mission_queue.get_all_missions()),
            "No queda ninguna EXPORT fantasma colgada")

        # (c) la recarga termina: AMR_06 vuelve a IDLE y retoma el EXPORT pendiente
        amr6.bateria = 100.0
        amr6.tarea_actual = None
        amr6.estado = "IDLE"
        env._dispatch_exports()
        self.assertEqual(amr6.tarea_actual.tipo, "EXPORT", "AMR_06 retoma la entrega tras recargar")

        # (d) ciclo real de entrega completa: recoge del OUT (LOADING→out_pickup) y entrega en
        # el muro (UNLOADING→out_ship) → OUT drena a 0, sin nada colgado
        amr6.posicion_nodo = "OUT"
        amr6.x, amr6.y = env.node_positions["OUT"]
        amr6.estado = "LOADING"
        amr6.loading_timer = 0.05
        amr6.step(
            dt_sim=0.1, G=env.G, obstacles=[], metrics_manager=env.metrics,
            generator_manager=env.generator, sim_time=200.0, env=env,
        )  # parado en OUT: LOADING completa → out_pickup (stock−1)
        self.assertEqual(env.out_stock["OUT"], 0, "AMR_06 recogió el paquete del OUT")
        amr6.posicion_nodo = "MURO_ENTREGA"
        amr6.x, amr6.y = env.node_positions["MURO_ENTREGA"]
        amr6.estado = "UNLOADING"
        amr6.loading_timer = 0.05
        amr6.step(
            dt_sim=0.1, G=env.G, obstacles=[], metrics_manager=env.metrics,
            generator_manager=env.generator, sim_time=260.0, env=env,
        )  # parado en el muro: UNLOADING completa → out_ship (en_ruta−1, entrega hecha)
        self.assertEqual(env.out_stock["OUT"], 0, "Buffer del OUT vacío al final")
        self.assertEqual(env.out_en_ruta["OUT"], 0, "Sin entrega colgada: el OUT drena por completo")
        pend = [m for m in env.mission_queue.get_all_missions()
                if m.tipo == "EXPORT" and m.estado in ("pendiente", "asignada", "en_curso")]
        self.assertEqual(len(pend), 0, "Ninguna EXPORT colgada")

    def test_02_abort_export_tras_recoger_devuelve_paquete(self):
        """Si el EXPORT se aborta YA con paquete recogido (estado 'en_curso'), el paquete vuelve
        al buffer y se reprograma; y el KPI de espera en OUT se mide desde el nuevo arribo."""
        env = self.env
        env.out_arrive("OUT", 100.0)
        amr6 = self._amr6()
        amr6.posicion_nodo = "OUT"
        amr6.x, amr6.y = env.node_positions["OUT"]
        amr6.estado = "LOADING"
        amr6.loading_timer = 0.05
        amr6.tarea_actual = env.mission_queue.get_all_missions()[-1]
        amr6.step(
            dt_sim=0.1, G=env.G, obstacles=[], metrics_manager=env.metrics,
            generator_manager=env.generator, sim_time=100.0, env=env,
        )  # LOADING completa → out_pickup (stock 1→0, paquete en vuelo 'en_curso')
        self.assertEqual(env.out_stock["OUT"], 0, "Paquete recogido del buffer")
        self.assertEqual(amr6.tarea_actual.estado, "en_curso", "EXPORT en vuelo hacia el muro")

        # batería cae mientras viaja → recarga prioritaria interrumpe la EXPORT en vuelo
        amr6.bateria = 12.0
        env._auto_recharge_check()
        # FIX: el paquete recogido vuelve al buffer (no se pierde) y se reprograma el EXPORT
        self.assertEqual(env.out_stock["OUT"], 1, "El paquete recogido vuelve al buffer del OUT")
        self.assertEqual(env.out_en_ruta["OUT"], 1, "EXPORT reprogramada")
        self.assertEqual(len(self._pend_exp("OUT")), 1)
        self.assertTrue(amr6.tarea_actual is None or amr6.tarea_actual.tipo == "RECHARGE",
                        "El AMR ahora va a cargar")

    def test_03_kpi_tiempo_medio_en_out(self):
        """KPI: tiempo medio de paquetes en OUTs previo a la entrega al muro. Un paquete que
        llega en t=100s y se entrega en t=160s → promedio = 1.0 min, expuesto en el snapshot."""
        env = self.env
        env.sim_time = 100.0
        env.out_arrive("OUT", 100.0)
        env.out_arrive("OUT_2", 100.0)
        # primer paquete se entrega a los 30 s (t=130)
        env.sim_time = 130.0
        export1 = [m for m in env.mission_queue.get_all_missions()
                   if m.tipo == "EXPORT" and m.origen == "OUT"][0]
        export1.estado = "en_curso"
        env.out_pickup("OUT")
        env.out_ship("OUT")
        export1.estado = "completada"
        # segundo paquete se entrega a los 90 s (t=190)
        env.sim_time = 190.0
        export2 = [m for m in env.mission_queue.get_all_missions()
                   if m.tipo == "EXPORT" and m.origen == "OUT_2"][0]
        export2.estado = "en_curso"
        env.out_pickup("OUT_2")
        env.out_ship("OUT_2")
        export2.estado = "completada"

        self.assertEqual(env.metrics.out_pkgs_measured, 2)
        self.assertAlmostEqual(env.metrics.total_out_wait_sec, 30.0 + 90.0, places=6)
        snap = env.metrics.get_snapshot()
        self.assertAlmostEqual(snap.tiempo_medio_en_out_min, (30.0 + 90.0) / 2 / 60.0, places=2)

    def test_04_paquetes_llegados_durante_carga_se_entregan_al_volver(self):
        """Regresión del escenario reportado: el AMR exclusivo está CHARGING mientras llegan
        paquetes a los OUTs → esos EXPORT quedan pendientes; al volver a IDLE, AMR_06 los
        entrega todos (ninguno queda 'olvidado')."""
        env = self.env
        amr6 = self._amr6()
        amr6.estado = "CHARGING"          # carga en curso
        amr6.bateria = 55.0
        # durante la carga llegan paquetes a dos OUTs
        env.out_arrive("OUT", 150.0)
        env.out_arrive("OUT_2", 151.0)
        self.assertEqual(env.out_en_ruta["OUT"], 1)
        self.assertEqual(env.out_en_ruta["OUT_2"], 1)

        # termina la carga → IDLE en el muro
        amr6.estado = "IDLE"
        amr6.bateria = 100.0
        amr6.posicion_nodo = "MURO_ENTREGA"
        amr6.x, amr6.y = env.node_positions["MURO_ENTREGA"]
        env._dispatch_exports()
        self.assertEqual(amr6.tarea_actual.tipo, "EXPORT", "Al volver de cargar, AMR_06 retoma las entregas")

        # consume la primera EXPORT
        exp1 = amr6.tarea_actual
        exp1.estado = "en_curso"
        env.out_pickup(exp1.origen)
        env.out_ship(exp1.origen)
        exp1.estado = "completada"
        amr6.tarea_actual = None
        amr6.estado = "IDLE"
        env._dispatch_exports()
        self.assertEqual(amr6.tarea_actual.tipo, "EXPORT", "El segundo paquete pendiente también se entrega")
        exp2 = amr6.tarea_actual
        exp2.estado = "en_curso"
        env.out_pickup(exp2.origen)
        env.out_ship(exp2.origen)
        exp2.estado = "completada"

        self.assertEqual(env.out_stock["OUT"], 0)
        self.assertEqual(env.out_stock["OUT_2"], 0)
        self.assertEqual(env.out_en_ruta["OUT"], 0)
        self.assertEqual(env.out_en_ruta["OUT_2"], 0)

if __name__ == "__main__":
    unittest.main()
