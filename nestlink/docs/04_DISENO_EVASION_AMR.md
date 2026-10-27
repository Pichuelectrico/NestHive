# Diseño técnico — Ronda 8: evasión y cesión de paso AMR↔AMR

**Autor:** Cursor (diseño) · **Implementación:** Antigravity  
**Estado:** propuesta para implementación · **Ámbito:** backend (`app/sim/`)  
**Restricciones:** determinista (`random.seed(42)`), no romper tests existentes (45/45), contrato WS aditivo, frontend intacto por defecto.

---

## 1. Resumen ejecutivo

Los AMRs deben **esquivarse** en cabeceo (direcciones opuestas en la misma arista) reutilizando la mecánica PEM ya existente para peatones (`WAITING_OBSTACLE`), con **prioridad de misión** y **re-ruteo A\*** cuando hay alternativa. En la **misma dirección** sobre la misma arista **no** se frena: pueden transitar a velocidad plena (sin cambio).

El algoritmo se ejecuta **antes** del bucle `amr.step()` en cada tick del `SimulationEnvironment`, en orden determinista por `amr.id`, para evitar condiciones de carrera intra-tick.

---

## 2. Modelo de detección de conflicto

### 2.1 Datos disponibles en el estado actual

Por cada `AMRAgent` en `env.amrs` (tick `t`, `dt_sim` ya calculado):

| Campo | Uso |
|-------|-----|
| `id`, `nombre` | Tie-break, notices |
| `x`, `y` | Posición continua (px; **10 px = 1 m**) |
| `posicion_nodo` | Nodo discreto “anclado” al completar un salto de arista |
| `path`, `target_node_idx` | Ruta restante y siguiente nodo |
| `velocidad_ms` | Velocidad nominal (m/s) |
| `estado` | Solo conflictos si `MOVING_TO_PICKUP` o `MOVING_TO_DELIVERY` (y opcionalmente `REROUTING` en tránsito) |
| `tarea_actual` | `prioridad`, `tipo`, `destino`, `origen` |
| `angulo` | Dirección de movimiento (validación auxiliar) |

Del entorno:

| Campo | Uso |
|-------|-----|
| `sim_time`, `tick_id` | Ventanas temporales, notices |
| `dt_sim` | `TICK_INTERVAL_SEC × SIM_SPEED_FACTOR` = **0,8 s sim/tick** a 5 Hz y factor 4 |
| `G` (NetworkX) | Aristas, `weight`/`length`, `blocked` |
| `node_positions` | Geometría para distancias y tiempos |
| `node_types` | No usado en conflicto AMR↔AMR (solo cargadores) |

**Paso de cinemática actual** (`agents.py`):

```text
step_dist_px = velocidad_ms × 10.0 × dt_sim
```

Ejemplo: `1,5 m/s × 10 × 0,8 = 12 px/tick` ≈ **1,2 m/tick sim**.

### 2.2 Arista activa de un AMR

Función `get_active_edge(amr) → Optional[Tuple[str, str]]`:

1. Si `estado` no es movimiento → `None`.
2. Si `path` vacío o `target_node_idx >= len(path)` → `None`.
3. `to_node = path[target_node_idx]`.
4. `from_node = path[target_node_idx - 1]` si `target_node_idx > 0`, else `posicion_nodo`.
5. Si `from_node == to_node` → `None`.
6. Retornar arista dirigida `(from_node, to_node)`.

**Progreso en arista** `edge_progress(amr) → float` en `[0, 1]`:

- `tx, ty = node_positions[to_node]`
- `dist_remaining_px = hypot(tx - x, ty - y)`
- `edge_len_px = hypot(tx - fx, ty - fy)` con `fx, fy` de `from_node`
- `progress = 1 - (dist_remaining_px / edge_len_px)` (clamp 0–1)

### 2.3 Conflicto cabeceo (head-on)

Dos AMRs **A** y **B** están en **conflicto cabeceo** si:

1. `edge_A = (u, v)` y `edge_B = (v, u)` — misma arista física, **direcciones opuestas**.
2. Ambos en estado de movimiento (ver §2.1).
3. **Ventanas de ocupación solapadas** en tiempo sim:

Estimar tiempo hasta **salir** de la zona de conflicto (nodo compartido del cabeceo):

```text
time_clear_A = (dist_remaining_A_px / 10.0) / velocidad_ms_A   # segundos sim
time_clear_B = (dist_remaining_B_px / 10.0) / velocidad_ms_B
time_enter_opposite = max(0, (dist_to_meeting_px / 10.0) / velocidad_ms)  # opcional refinamiento
```

**Criterio simplificado (recomendado para MVP):**

- Conflicto si ambos tienen `progress < 0.95` (aún no han “pasado” el cruce) **y**
- `max(time_clear_A, time_clear_B) > min(time_clear_A, time_clear_B) - ε` con `ε = 0` (solapamiento total en arista estrecha).

**Criterio robusto (recomendado en diseño):**

- Calcular `t_enter_A`, `t_leave_A` y `t_enter_B`, `t_leave_B` respecto al **punto medio** de la arista (o al nodo `u`/`v` más cercano al encuentro).
- Conflicto si los intervalos `[t_enter, t_leave]` se solapan.

**Margen PEM (≥ 2 ticks):**

- Activar resolución si el solapamiento ocurre en `≤ lookahead_sim = 2 × dt_sim = **1,6 s**` **o** si la distancia entre posiciones continuas `< conflict_radius_m`.
- `conflict_radius_m = 2.5` (igual radio que peatón `ObstaculoState.radius` por defecto).

### 2.4 Misma dirección — **NO es conflicto**

Si `edge_A = (u, v)` y `edge_B = (u, v)`:

- **No aplicar** cesión ni frenado.
- **No modificar** velocidad ni estado.
- Los AMRs pueden compartir la arista a plena velocidad (modelo “paso lado a lado” abstracto).

**Confirmación explícita:** no introducir colisión física ni slow-down en co-dirección; el test debe verificar que ningún AMR entra en `WAITING_OBSTACLE` por este caso.

### 2.5 Reutilización PEM (peatón → AMR “como humano”)

Mecánica actual en `AMRAgent.step()` (líneas 77–93):

```python
dist_m = sqrt((obs.x - x)^2 + (obs.y - y)^2) / 10.0
if dist_m < obs.radius → WAITING_OBSTACLE; return (sin mover)
```

**Inserción sin romper el ciclo:**

1. **Opción A (preferida):** módulo `AmrYieldResolver` en `env.run_loop` **antes** de `amr.step()`:
   - Detecta conflictos cabeceo.
   - Resuelve prioridad.
   - Al perdedor: o bien **re-rutea** (`REROUTING` + nuevo `path`), o bien fuerza `estado = WAITING_OBSTACLE` y **no llama** a `_move_along_path` ese tick (equivalente a peatón).
2. **Opción B (alternativa):** inyectar obstáculos sintéticos `OPERATOR` en la posición `(x, y)` del AMR ganador con `radius = conflict_radius_m` solo para el AMR perdedor — reutiliza el bloque PEM existente sin duplicar lógica.

**Recomendación:** Opción A para resolución determinista centralizada; Opción B solo como fallback local si el perdedor ya está en mitad de arista y debe “ver” al otro como peatón móvil.

El AMR que **cede** trata al otro como entidad móvil en su radio → sensación “le doy el rol del humano al otro”.

---

## 3. Política de cesión determinista (sin deadlock)

### 3.1 Quién gana / quién cede

Para un par en conflicto cabeceo `(A, B)`:

1. **Prioridad de misión:** `prio = tarea_actual.prioridad` (entero; mayor gana). Misiones `RECHARGE` = 8, `SUPPLY_REQUEST` urgente = 10, etc.
2. Si sin tarea: prioridad efectiva = `0` (IDLE en movimiento es raro; tratar como 0).
3. **Tie-break 1:** menor **distancia restante** al destino de la fase actual (suma euclidiana px de nodos restantes en `path[target_node_idx:]` → metros).
4. **Tie-break 2:** `amr.id` lexicográfico menor gana (determinista).

El **perdedor** `L`, el **ganador** `W`.

### 3.2 Acciones del perdedor

Orden de intentos (una sola acción por tick de resolución):

| Condición | Acción |
|-----------|--------|
| `L` en nodo (`progress < 0.05`) o aún no entró en arista conflictiva | **(a) Re-ruteo:** `find_shortest_path_excluding_edge(G, current, dest, exclude=(u,v))`. Si existe path → `path = new_path`, `target_node_idx = 1`, `estado = REROUTING` → luego `MOVING_*`. Notice opcional `INFO`: “Re-ruteo por conflicto con {W.nombre}”. |
| Re-ruteo imposible o `progress ≥ 0.05` (mitad de arista) | **(b) Espera:** `estado = WAITING_OBSTACLE`, no mover este tick. Notice `INFO` o tipo nuevo: “{L.nombre} cediendo paso a {W.nombre}”. |
| `L` ya en `WAITING_OBSTACLE` | Mantener hasta que `W` abandone la arista conflictiva (ver §3.4). |

**No** reducir `velocidad_ms` permanentemente en MVP; “disminuir velocidad” se modela como **espera en nodo** (`WAITING_OBSTACLE`), coherente con peatones.

### 3.3 Anti-deadlock

- La regla de prioridad es **antisimétrica**: un solo ganador por par.
- Tie-break por `id` garantiza decisión única si prioridad y distancia iguales.
- **Nunca** ambos ceden por la misma regla: solo el perdedor cambia estado.
- Al liberar: cuando `W` completa la arista (`progress_W > 0.95` o `posicion_nodo` cambió), `L` en `WAITING_OBSTACLE` vuelve a `MOVING_*` (lógica ya existente líneas 92–93).

### 3.4 Umbrales recomendados

| Parámetro | Valor | Notas |
|-----------|-------|-------|
| `lookahead_sim` | `2 × dt_sim` = **1,6 s** | ≥ 2 ticks de margen |
| `conflict_radius_m` | **2,5 m** | Igual que peatón |
| `progress_mid_edge` | **0,05 / 0,95** | Umbral nodo vs mitad |
| `ε_overlap` | **0,1 s** | Solapamiento temporal mínimo |

---

## 4. Integración con código existente

### 4.1 Archivos nuevos

| Archivo | Responsabilidad |
|---------|-----------------|
| `app/sim/amr_yield.py` | `get_active_edge`, `detect_head_on_conflicts`, `resolve_yield`, `find_shortest_path_excluding_edge` |

### 4.2 Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `app/sim/env.py` | En `run_loop`, **entre** paso 4 (peatones) y paso 5 (cinemática): llamar `AmrYieldResolver.step(self.amrs, self.G, self.node_positions, self.sim_time, dt_sim)` |
| `app/sim/routing.py` | `find_shortest_path_excluding_edge(G, source, target, node_positions, exclude_edge: Tuple[str,str])` — temporalmente marcar arista `(u,v)` y `(v,u)` como bloqueadas solo para esa búsqueda (no mutar `G` global) |
| `app/sim/agents.py` | **Mínimo:** opcional flag `cediendo_paso: bool` leído en `get_state()`. **No** nuevo estado FSM si reusamos `WAITING_OBSTACLE`. |
| `app/models.py` | `AMRState.cediendo_paso: Optional[bool] = False` (aditivo) |

### 4.3 Flujo del tick (orden crítico)

```text
1. generator.step
2. _auto_recharge_check
3. reubicación IDLE
4. asignación húngara
5. obstacle_manager.step → active_obstacles
6. ★ amr_yield_resolver.resolve(env)   # NUEVO — orden AMRs sorted by id
7. for amr in amrs: amr.step(...)      # PEM peatones + FSM existente
8. broadcast snapshot
```

**Orden determinista en `resolve`:** iterar conflictos en pares `(i,j)` con `id[i] < id[j]`; aplicar resolución inmediatamente para que el segundo conflicto vea el estado actualizado del primero.

### 4.4 Estados FSM — reutilizar, no expandir

| Situación | Estado |
|-----------|--------|
| Cede en nodo / sin alternativa | `WAITING_OBSTACLE` (existente) |
| Re-ruteo por conflicto | `REROUTING` → `MOVING_TO_PICKUP` / `MOVING_TO_DELIVERY` (existente) |
| Avanza con prioridad | Sin cambio |

**No** añadir `YIELDING` al enum `EstadoAMR` salvo necesidad futura de UI; el front ya colorea `WAITING_OBSTACLE`.

### 4.5 Snapshot / contrato WebSocket (aditivo)

```python
class AMRState(BaseModel):
    ...
    cediendo_paso: bool = False  # True si WAITING_OBSTACLE por conflicto AMR este tick
```

- Frontend `lib/types.ts`: `cediendo_paso?: boolean` (opcional; ignorado si falta).
- **Notices:** `add_notice("INFO", None, f"{L.nombre} cediendo paso a {W.nombre}")` — suficiente para demo sin cambio de UI.
- Tipo dedicado `YIELD` en notices es opcional y aditivo.

### 4.6 Compatibilidad `SIM_SPEED_FACTOR = 4` y 5 Hz

- `dt_sim = 0,8 s` → detección con `lookahead = 1,6 s` cubre **2 ticks** de sim antes del encuentro.
- A `1,5 m/s`, en 1,6 s un AMR avanza ~2,4 m — suficiente para activar cesión antes del “zona roja”.
- Resolver **antes** de `step` evita que dos AMRs se muevan en el mismo tick hacia el choque.

---

## 5. Plan de tests (`tests/test_round8.py`)

Antigravity debe implementar **sin romper** los 45 tests actuales. Suite nueva independiente o ampliación; objetivo **45 + N** verdes.

| # | Nombre del test | Assertion clave |
|---|-----------------|-----------------|
| 1 | `test_01_head_on_one_yields_no_deadlock` | Dos AMRs con paths opuestos en `X_02↔X_05`; tras K ticks, uno en `WAITING_OBSTACLE` o `REROUTING`, el otro avanza; ambos eventualmente `IDLE` o completan misión; **ninguno** permanece en `WAITING_OBSTACLE` > 30 s sim |
| 2 | `test_02_same_direction_no_yield` | Dos AMRs misma arista `(u→v)`; **nunca** `WAITING_OBSTACLE` atribuible a conflicto AMR; ambos mantienen `MOVING_*` |
| 3 | `test_03_priority_p10_beats_p8` | AMR con misión P10 vs P8 en cabeceo; P8 cede (`WAITING_OBSTACLE` o reroute); P10 sigue en `MOVING_*` |
| 4 | `test_04_tiebreak_by_remaining_distance` | Misma prioridad; AMR más lejos del destino cede |
| 5 | `test_05_tiebreak_by_amr_id` | Misma prioridad y distancia; `AMR_01` gana sobre `AMR_02` (id menor) |
| 6 | `test_06_same_tick_organic_no_duplicate_charger_style_race` | Dos AMRs forzados a cabeceo en **un solo** `resolve()`; decisiones distintas; sin estado inconsistente en `path` |
| 7 | `test_07_reroute_when_alternate_path_exists` | Con arista alternativa en grafo, perdedor en nodo obtiene `REROUTING` y `path` no contiene arista conflictiva |

**Setup común:** `sim_env.select_plant("quito")`, `random.seed(42)`, posiciones iniciales controladas vía atributos de `AMRAgent` o misiones forzadas.

**Firma ejemplo test 3:**

```python
def test_03_priority_p10_beats_p8(self):
    ...
    self.assertEqual(winner.estado, "MOVING_TO_DELIVERY")
    self.assertIn(loser.estado, ("WAITING_OBSTACLE", "REROUTING"))
```

---

## 6. Hitos de implementación (Antigravity)

| Hito | Tamaño | Contenido | Riesgo |
|------|--------|-----------|--------|
| **H1** | S | `get_active_edge`, detección cabeceo, tests 2 y 6 (solo detección, sin resolver) | Bajo |
| **H2** | M | `find_shortest_path_excluding_edge` + política prioridad/tie-break + `resolve()` en `env.run_loop` | Medio |
| **H3** | M | Re-ruteo perdedor + `WAITING_OBSTACLE` + notices; tests 1, 3, 4, 5, 7 | Medio |
| **H4** | S | Campo `cediendo_paso` en modelo/snapshot; test snapshot opcional | Bajo |
| **H5** | S | Regresión completa `pytest tests/` 45+N; ajuste umbrales si flaky | Medio |

**Orden:** H1 → H2 → H3 → H4 → H5.

**Riesgos principales:**

1. **Orden intra-tick:** resolver antes de `step` (mitigado en diseño).
2. **Re-ruteo mutando `G`:** usar exclusión temporal en A*, no `block_edge` global.
3. **Flaky tests:** usar posiciones fijas y `dt_sim` conocido; evitar dependencia de peatones aleatorios (mockear `obstacles=[]` en tests de conflicto).

---

## 7. Pseudocódigo de referencia

```python
def resolve_amr_conflicts(env, dt_sim):
    amrs = sorted(env.amrs, key=lambda a: a.id)
    conflicts = detect_head_on_pairs(amrs, env.node_positions, lookahead=2*dt_sim)

    for (a, b) in conflicts:
        winner, loser = pick_winner(a, b)  # prioridad → distancia → id
        if loser.estado not in ("MOVING_TO_PICKUP", "MOVING_TO_DELIVERY"):
            continue
        u, v = get_active_edge(loser)
        dest = loser.tarea_actual.destino if loser.estado == "MOVING_TO_DELIVERY" else loser.tarea_actual.origen
        alt = find_shortest_path_excluding_edge(env.G, loser.posicion_nodo, dest, env.node_positions, (u, v))
        if alt and edge_progress(loser) < 0.05:
            loser.path = alt
            loser.target_node_idx = 1
            loser.estado = "REROUTING"
            env.add_notice("INFO", None, f"Re-ruteo {loser.nombre} por conflicto con {winner.nombre}")
        else:
            loser.estado = "WAITING_OBSTACLE"
            loser.cediendo_paso = True
            env.add_notice("INFO", None, f"{loser.nombre} cediendo paso a {winner.nombre}")
```

En `get_state()`, `cediendo_paso = (estado == WAITING_OBSTACLE and self.cediendo_paso_flag)`; limpiar flag al salir de espera.

---

## 8. Fuera de alcance (R8)

- Colisión física / empuje / geometría de dos AMRs en paralelo con ancho de pasillo.
- Slow-down proporcional de velocidad (solo espera o re-ruteo).
- Cambios en `PlantMap.tsx` o render de trayectorias (OpenCode / frontend).
- Modificación del asignador húngaro (conflictos se resuelven en ejecución, no en planificación global).

---

## 9. Referencias de código actual

- Peatón PEM: `agents.py:77–93`
- Cinemática arista: `agents.py:188–218`, `step_dist = velocidad_ms * 10.0 * dt_sim`
- Re-ruteo por bloqueo: `agents.py:191–198`
- Tick engine: `env.py:93–145`, `dt_sim = 0.2 * 4.0`
- A*: `routing.py:find_shortest_path`
- Prioridad misiones: `assignment.py` (`prioridad` en `Tarea`)
- Snapshot: `env.py:get_snapshot`, `models.py:AMRState`

---

*Documento listo para implementación por Antigravity. Cursor no modifica código de simulación en esta ronda.*
