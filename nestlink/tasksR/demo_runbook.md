# 📋 Runbook live-day — Demo NestHive (Reto 1) · realistic
> 4-sep 18:30 · Salón Azul USFQ · Pitch 5 min (`tasksR/pitch_5min.md`) + 2 min Q&A · demo default = `realistic` (commit cabeaa0)

## 1) Pre-flight (5 min antes)
- [ ] Rama `JoshR` actualizada (lead pushea; `git pull` si hace falta).
- [ ] Docker corriendo · puertos 8000/3000 libres (`lsof -ti:8000,3000`).
- [ ] `cd ~/Desktop/Proyect/NestLink && docker compose ps` → `api (healthy)` y `web` Up.
- [ ] **Default realistic:** `curl -s localhost:8000/health` → `"plant":"realistic"` y `sim_running:true`.
- [ ] Layout OK: `curl -s localhost:8000/api/v1/layout` → título "Planta Realistic — NestHive", **75 nodos**, nodo `OUT`, **walls** (2 muros) presentes.
- [ ] Flota y ciclo vivo: `/api/v1/fleet` = 5 AMRs; `/api/v1/missions` muestra `SUPPLY_REQUEST`+`PICKUP_PT`+`EXPEDITION`; `/api/v1/metrics` → `viajes_completados` creciendo.

## 2) Cheat-sheet de arranque
```bash
docker compose up -d            # arranque rápido
docker compose up --build -d    # si cambió código (NEXT_PUBLIC_* son build-ARG → siempre --build)
docker compose logs -f api      # logs backend (Ctrl+C para salir)
```
- Si **no arranca en realistic** (planta distinta/imagen vieja):
```bash
curl -s -X POST localhost:8000/api/v1/sim/select -H 'Content-Type: application/json' -d '{"plant":"realistic"}'
```
y en la web: selector de planta → «Planta Realistic» o `F5`.

## 3) Guion cronometrado 5 min (resumen de pitch_5min.md)
| Tiempo | Qué decir / hacer |
|---|---|
| 0:00–0:40 | Problema: AMRs que no se hablan → esperas, choques, gente desbloqueando robots. |
| 0:40–1:15 | Solución: capa de coordinación/visibilidad, flota unificada, cerebro que nunca deja un robot esperando forever. |
| 1:15–3:15 | **Demo en vivo (fullscreen F11, LiDAR ON):** 1) MP entra por el este → SUPPLY_REQUEST a líneas. 2) 4 líneas procesan → cada ~20 s un paquete. 3) AMR lo lleva a **Paletizado**. 4) Se expide a **OUT (centro)** → fin del recorrido. 5) Barrido **LiDAR cian** = percepción real. 6) **Peatones** → re-ruteo sin parar producción. Dejar ver **1 ciclo completo** antes de cortar. |
| 3:15–4:00 | Métricas: viajes completados, tiempo medio entrega, paradas/km evitados, ROI. |
| 4:00–4:40 | Diferenciales: flota heterogénea unificada, percepción real con LiDAR, tolerancia a humanos. |
| 4:40–5:00 | Cierre + dejar el mapa en pantalla. **Q&A:** 5 preguntas preparadas (pitch_5min.md §Q&A). |

> Flota roja unificada `#E4032E` y LiDAR ON por defecto en realistic — verificar antes de salir.

## 4) Contingencias rápidas
- **AMR atascado / no avanza:** normal que espere a peatón; si >90 s sim se descongela solo (anti-freeze). Si persiste → `docker compose restart api`.
- **Sim no avanza / sin ciclo de paquete:** darle 30–60 s (PICKUP_PT = cada ~20 s sim). Si falta `EXPEDITION`/`OUT` → imagen vieja: `docker compose up --build -d`.
- **Web offline / WS no conecta:** `F5` → `docker compose restart web` → último recurso modo offline `Ctrl+Shift+D`.
- **Rebuild api/web:** `docker compose up --build -d` (reconstruye ambos desde los commits).
- **Puertos ocupados:** `lsof -ti:8000,3000 | xargs kill -9` y `docker compose up -d`.

## 5) Checklist de cierre
- [ ] Detener demo: `docker compose down` (sin borrar imágenes) y dejar el mapa en pantalla si hay Q&A.
- [ ] Sin procesos colgados (`docker compose ps` → abajo) · pantalla fuera de No Molestar.
- [ ] Anotar métricas mostradas (viajes completados, ROI) por si piden datos en Q&A.

---
*Runbook conciso generado por Deep · 4-sep-2026 · validado en vivo (stack arriba, plant:"realistic", walls presentes, ciclo SUPPLY→PICKUP_PT→EXPEDITION activo).*
