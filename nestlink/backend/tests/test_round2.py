import unittest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.sim.env import sim_env

class TestRound2Enhancements(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        sim_env.select_plant("quito")

    def test_01_multi_plant_catalog(self):
        """Verifica el endpoint GET /api/v1/plants y la disponibilidad de Quito y Guayaquil."""
        response = self.client.get("/api/v1/plants")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("plants", data)
        plant_ids = [p["id"] for p in data["plants"]]
        self.assertIn("quito", plant_ids)
        self.assertIn("cd_guayaquil", plant_ids)

    def test_02_layout_by_plant(self):
        """Verifica la carga de layouts específicos por parámetro query."""
        resp_quito = self.client.get("/api/v1/layout?plant=quito")
        self.assertEqual(resp_quito.status_code, 200)
        self.assertEqual(len(resp_quito.json()["nodes"]), 24)

        resp_gye = self.client.get("/api/v1/layout?plant=cd_guayaquil")
        self.assertEqual(resp_gye.status_code, 200)
        self.assertEqual(len(resp_gye.json()["nodes"]), 30)

    def test_03_switch_plant_simulation(self):
        """Verifica la conmutación dinámica del motor a CD Guayaquil y que /layout sin param devuelva la activa."""
        resp = self.client.post("/api/v1/sim/select", json={"plant": "cd_guayaquil"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["plant"], "cd_guayaquil")
        self.assertEqual(sim_env.plant_id, "cd_guayaquil")
        self.assertEqual(len(sim_env.amrs), 6) # Guayaquil tiene 6 AMRs

        # TEST CRÍTICO FIX 2.1: /layout sin param debe devolver Guayaquil (27 nodos)
        resp_active = self.client.get("/api/v1/layout")
        self.assertEqual(resp_active.status_code, 200)
        self.assertEqual(len(resp_active.json()["nodes"]), 30, "El endpoint /layout sin param debe reflejar la planta activa.")

        # Verificar que el snapshot contiene el campo 'plant'
        snap = sim_env.get_snapshot()
        self.assertEqual(snap.plant, "cd_guayaquil")

        # Volver a Quito
        resp2 = self.client.post("/api/v1/sim/select", json={"plant": "quito"})
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(sim_env.plant_id, "quito")
        self.assertEqual(len(sim_env.amrs), 5)
        
        resp_active_quito = self.client.get("/api/v1/layout")
        self.assertEqual(len(resp_active_quito.json()["nodes"]), 24)
        snap_quito = sim_env.get_snapshot()
        self.assertEqual(snap_quito.plant, "quito")

    def test_04_peak_demand_forced_mission_and_notice_persistence(self):
        """Verifica que el pico de demanda drene la línea, cree misión SUPPLY_REQUEST y el notice persista."""
        initial_missions_count = len(sim_env.mission_queue.get_all_missions())
        
        resp = self.client.post("/api/v1/sim/peak", json={"line_id": "E1_IN", "drain_pct": 35.0})
        self.assertEqual(resp.status_code, 200)
        
        # Verificar que se creó una nueva misión urgente visible en /api/v1/missions
        resp_missions = self.client.get("/api/v1/missions")
        self.assertEqual(resp_missions.status_code, 200)
        missions = resp_missions.json()
        self.assertGreater(len(missions), initial_missions_count)
        latest = missions[0]
        self.assertEqual(latest["tipo"], "SUPPLY_REQUEST")
        self.assertEqual(latest["destino"], "E1_IN")
        self.assertEqual(latest["prioridad"], 10)

        # TEST CRÍTICO FIX 2.1: Verificar que el notice persiste en snapshots sucesivos
        snap1 = sim_env.get_snapshot()
        self.assertTrue(any(n.tipo == "PEAK" for n in snap1.notices))
        
        # Simular avance de 5 ticks (1 segundo)
        for _ in range(5):
            sim_env.sim_time += 0.8
            sim_env.tick_id += 1
            
        snap2 = sim_env.get_snapshot()
        self.assertTrue(any(n.tipo == "PEAK" for n in snap2.notices), "El notice debe persistir durante varios ticks")

    def test_05_fleet_home_zone_affinity(self):
        """Verifica que los AMRs tengan su home_zone configurada para asignación natural."""
        amr1 = next(a for a in sim_env.amrs if a.id == "AMR_01")
        amr2 = next(a for a in sim_env.amrs if a.id == "AMR_02")
        self.assertEqual(amr1.home_zone, "L1_OUT")
        self.assertEqual(amr2.home_zone, "E1_IN")

    def test_06_notices_in_snapshot(self):
        """Verifica que notices esté presente en el snapshot para el front."""
        sim_env.add_notice("INFO", None, "Prueba de notice")
        snap = sim_env.get_snapshot()
        self.assertIsInstance(snap.notices, list)
        self.assertGreaterEqual(len(snap.notices), 1)

if __name__ == "__main__":
    unittest.main()
