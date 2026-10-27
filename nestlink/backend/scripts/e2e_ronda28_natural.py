import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.sim.env import SimulationEnvironment

random.seed(11)
env = SimulationEnvironment("realistic")
env.obstacle_manager.pedestrians = []

for t in range(2500):
    env.step_tick()

snap = env.metrics.get_snapshot()
shipped = env.metrics.out_pkgs_measured
print(f"2500 ticks seed 11 (sin forzar recarga)")
print(f"  paquetes medidos (out_ship completados): {shipped}")
print(f"  KPI tiempo_medio_en_out_min: {snap.tiempo_medio_en_out_min}")
print(f"  viajes_completados: {snap.viajes_completados}")
print(f"  out_stock final: {env.out_stock}")
print(f"  out_en_ruta final: {env.out_en_ruta}")
stuck = 0
for m in env.mission_queue.get_all_missions():
    if m.tipo == "EXPORT" and m.estado == "en_curso":
        owner = next((a for a in env.amrs if a.tarea_actual and a.tarea_actual.id == m.id), None)
        if owner is None or (owner.id == env.delivery_amr_id and owner.estado == "IDLE"):
            stuck += 1
print(f"  EXPORT en vuelo colgadas: {stuck}")
ok = shipped > 0 and snap.tiempo_medio_en_out_min > 0 and stuck == 0
print("RESULTADO:", "✅ OK" if ok else "❌ FALLO")
sys.exit(0 if ok else 1)
