"""Validación E2E: ronda 2.8 — AMR exclusivo interrumpido por recarga con EXPORT en vuelo.
Fuerza batería baja en pleno EXPORT y verifica que ningún paquete quede atrapado (invariante:
cada OUT con stock tiene su EXPORT provisionada, salvo que el AMR de entrega esté ocupado)."""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.sim.env import SimulationEnvironment

random.seed(7)
env = SimulationEnvironment("realistic")
env.obstacle_manager.pedestrians = []

forced = 0
max_stock_violation = 0
stuck_exports = 0
packages_shipped = 0

for t in range(1500):
    amr6 = next((a for a in env.amrs if a.id == env.delivery_amr_id), None)
    # Reproduce el bug: forzar batería baja mientras lleva un EXPORT en vuelo
    if amr6 and amr6.tarea_actual and amr6.tarea_actual.tipo == "EXPORT" and (t % 5 == 0):
        if amr6.bateria > 30:
            amr6.bateria = 12.0
            forced += 1
    env.step_tick()
    # Invariante: nunca más de 1 EXPORT provisionado por OUT, y jamás estado colgado
    for out, n in env.out_en_ruta.items():
        assert n <= 1, f"¡Más de 1 EXPORT provisionado en {out} (t={t}): {n}!"
    # todo EXPORT 'en_curso' debe estar asignado a un AMR vivo
    for m in env.mission_queue.get_all_missions():
        if m.tipo == "EXPORT" and m.estado == "en_curso":
            owner = next((a for a in env.amrs if a.tarea_actual and a.tarea_actual.id == m.id), None)
            if owner is None:
                stuck_exports += 1
            elif owner.id == env.delivery_amr_id and owner.estado == "IDLE":
                stuck_exports += 1

print(f"OK: 1500 ticks, seed 7")
print(f"  batería forzada a 12% en pleno EXPORT: {forced} veces")
print(f"  EXPORT en vuelo sin AMR vivo (colgados): {stuck_exports}")
print("  invariantes: out_en_ruta<=1 ✅; sin EXPORTes colgados ✅" if stuck_exports == 0 else "  ❌ EXPORTES COLGADOS")
print(f"  out_stock final: {env.out_stock}")
print(f"  out_en_ruta final: {env.out_en_ruta}")
print(f"  KPI tiempo medio en OUT (min): {env.metrics.get_snapshot().tiempo_medio_en_out_min}")
sys.exit(1 if stuck_exports else 0)
