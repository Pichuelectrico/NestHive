import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env


class TestRound5_2_RestockYControlMisiones(unittest.TestCase):
    """Ronda 5.2: restock +20% por entrega, reset de misiones y ajuste ±5 del sistema."""

    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    # --- (a) Restock por entrega suma +20% (no +65%) ---
    def test_01_agents_usa_restock_20_por_entrega(self):
        """Regresión: en el UNLOADING de SUPPLY_REQUEST el amount_pct debe ser 20.0."""
        src = (Path(__file__).parent.parent / "app/sim/agents.py").read_text()
        # Localizar la rama UNLOADING que descarga insumos
        self.assertIn("amount_pct=20.0", src,
                      "agents.py debe usar restock_line(..., amount_pct=20.0) (+20% por viaje)")
        self.assertNotIn("amount_pct=65.0", src,
                         "Ya no debe quedar el valor antiguo de +65% por viaje")

    def test_02_restock_line_aplica_mas_20_pct(self):
        """Llamar restock_line con 20% sube la línea exactamente +20 (saturado a 100)."""
        line = next(l for l in sim_env.generator.lines if l.id == "E1_IN")
        line.nivel_pct = 30.0
        ok = sim_env.generator.restock_line("E1_IN", amount_pct=20.0)
        self.assertTrue(ok)
        self.assertAlmostEqual(line.nivel_pct, 50.0, places=6)

        # Saturación: desde 95% con +20 debe quedar en 100
        line.nivel_pct = 95.0
        sim_env.generator.restock_line("E1_IN", amount_pct=20.0)
        self.assertAlmostEqual(line.nivel_pct, 100.0, places=6)

    # --- (b) reset_missions deja solo el conjunto inicial y AMRs IDLE ---
    def test_03_reset_missions_deja_4_iniciales_y_amrs_idle(self):
        # Poblar el sistema con misiones extra y un AMR en curso
        sim_env.adjust_missions(5)
        r = self.client.post("/api/v1/sim/reset_missions")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ok")
        self.assertGreaterEqual(data["missions_clearadas"], 4)
        activas = data["activas"]
        self.assertEqual(len(activas), 4)

        tipos_destinos = {(m["tipo"], m["destino"]) for m in activas}
        self.assertEqual(tipos_destinos, {
            ("SUPPLY_REQUEST", "E1_IN"),
            ("SUPPLY_REQUEST", "L1_OUT"),
            ("SUPPLY_REQUEST", "E2_IN"),
            ("SUPPLY_REQUEST", "L2_OUT"),
        })
        # Orígenes por marca (no hardcodeados a WH_MP_2)
        origenes = {m["destino"]: m["origen"] for m in activas}
        self.assertEqual(origenes["E1_IN"], "WH_MP_1")
        self.assertEqual(origenes["L1_OUT"], "WH_MP_3")
        self.assertEqual(origenes["E2_IN"], "WH_MP_2")
        self.assertEqual(origenes["L2_OUT"], "WH_MP_4")

        # Los AMRs no cargando deben quedar IDLE sin tarea
        for amr in sim_env.amrs:
            if amr.estado not in ("CHARGING",):
                self.assertEqual(amr.estado, "IDLE")
                self.assertIsNone(amr.tarea_actual)
                self.assertEqual(amr.path, [])

    # --- (c) adjust +5 añade 5 misiones pendientes ---
    def test_04_adjust_mas_cinco_anade_5_pendientes(self):
        pend_before = len(sim_env.mission_queue.get_pending_missions())
        r = self.client.post("/api/v1/sim/adjust_missions", json={"delta": 5})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["delta"], 5)
        self.assertEqual(len(data["misiones_nuevas"]), 5)
        pend_after = len(sim_env.mission_queue.get_pending_missions())
        self.assertEqual(pend_after, pend_before + 5)

        for m in data["misiones_nuevas"]:
            self.assertEqual(m["tipo"], "SUPPLY_REQUEST")
            self.assertIn(m["estado"], ("pendiente",))

    # --- (d) adjust -5 elimina 5 pendientes SIN tocar las en curso ---
    def test_05_adjust_menos_cinco_quita_pendientes_sin_tocar_en_curso(self):
        sim_env.adjust_missions(5)  # 5 nuevas pendientes
        # Marcar una misión como "en_curso" (simula un AMR trabajando ya)
        missions = sim_env.mission_queue.get_all_missions()
        en_curso = next(m for m in missions if m.estado == "pendiente")
        en_curso.estado = "en_curso"
        en_curso.amr_asignado = "amr_test"

        pend_before = len(sim_env.mission_queue.get_pending_missions())
        r = self.client.post("/api/v1/sim/adjust_missions", json={"delta": -5})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["delta"], -5)
        self.assertEqual(data["removidas"], min(5, pend_before))
        pend_after = len(sim_env.mission_queue.get_pending_missions())
        self.assertEqual(pend_after, max(pend_before - 5, 0))

        # La misión en_curso NO debe haberse borrado
        resto = {m.id for m in sim_env.mission_queue.get_all_missions()}
        self.assertIn(en_curso.id, resto,
                      "adjust -5 nunca debe eliminar una misión 'en_curso'/asignada")

    # --- ajuste delta=0 no hace nada ---
    def test_06_adjust_delta_cero_no_roto(self):
        r = self.client.post("/api/v1/sim/adjust_missions", json={"delta": 0})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["delta"], 0)


if __name__ == "__main__":
    unittest.main()
