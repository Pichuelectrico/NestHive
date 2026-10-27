# Contrato Canónico de Integración API & WebSockets — NestLink (Reto 1)

> **Propósito:** Definir el contrato formal y exhaustivo entre el **Frontend (Next.js)** y el **Backend (FastAPI)** para garantizar el desarrollo en paralelo sin conflictos ni bloqueos durante el Hackathon InnoLabs Nestlé.

---

## 1. Esquema del Snapshot en Tiempo Real (WebSocket `/ws`)

El backend emite por WebSocket una trama JSON cada **200 ms (5 Hz)** con el estado integral de la planta. El frontend utiliza estas coordenadas para interpolar con suavidad a 60 fps (LERP en Canvas/SVG).

### 1.1 Estructura JSON Exacta

```json
{
  "sim_time": 142.6,
  "tick_id": 713,
  "amrs": [
    {
      "id": "AMR_01",
      "nombre": "Nescafé Shuttle",
      "estado": "MOVING_TO_DELIVERY",
      "x": 340.5,
      "y": 180.2,
      "angulo": 90.0,
      "bateria": 87,
      "tarea_asignada": "TSK_091",
      "path": ["X_05", "X_08", "E1_IN"],
      "tipo": "pallet_lifter"
    }
  ],
  "lines": [
    {
      "id": "L1_OUT",
      "nombre": "L1 Nescafé (PT)",
      "material": "Frasco Vidrio 200g",
      "nivel_pct": 78.5,
      "minutos_restantes": 24.2
    },
    {
      "id": "E1_IN",
      "nombre": "E1 Savoy (Insumos)",
      "material": "Film Laminado 120mm",
      "nivel_pct": 21.0,
      "minutos_restantes": 7.5
    }
  ],
  "obstacles": [
    {
      "id": "PED_01",
      "tipo": "OPERATOR",
      "x": 125.0,
      "y": 248.0,
      "radius": 2.5,
      "edge": null
    },
    {
      "id": "BLK_X02_X05",
      "tipo": "SPILL",
      "x": 400.0,
      "y": 160.0,
      "radius": 0.0,
      "edge": ["X_02", "X_05"]
    }
  ],
  "kpis": {
    "viajes_completados": 18,
    "viajes_vacios_evitados": 6,
    "paradas_evitadas": 2,
    "tiempo_medio_entrega_min": 2.4,
    "km_evitados": 4.8,
    "roi_km_pct": 33.3
  },
  "notices": [
    {
      "tipo": "PEAK",
      "line_id": "E1_IN",
      "mensaje": "Pico de demanda inyectado en E1 Savoy",
      "sim_time": 142.6
    }
  ]
}
```

### 1.2 Definición de Tipos TypeScript

```typescript
export type EstadoAMR =
  | "IDLE"
  | "MOVING_TO_PICKUP"
  | "LOADING"
  | "MOVING_TO_DELIVERY"
  | "UNLOADING"
  | "WAITING_OBSTACLE"
  | "REROUTING"
  | "CHARGING"
  | "ERROR";

export type TipoAMR = "pallet_lifter" | "towing_tug" | "unit_load";

export type TipoObstaculo = "OPERATOR" | "SPILL" | "BLOCK";

export interface AMRState {
  id: string;
  nombre: string;
  estado: EstadoAMR;
  x: number;
  y: number;
  angulo: number; // Grados 0-360 para orientar sprite en canvas
  bateria: number; // 0-100%
  tarea_asignada: string | null;
  path: string[]; // Lista de IDs de nodos futuros
  tipo: TipoAMR;
}

export interface LineaState {
  id: string;
  nombre: string;
  material: string;
  nivel_pct: number; // 0-100%
  minutos_restantes: number;
}

export interface ObstaculoState {
  id: string;
  tipo: TipoObstaculo;
  x: number;
  y: number;
  radius: number; // Metros de radio de seguridad
  edge: [string, string] | null; // [node_from, node_to] si es bloqueo de arista
}

export interface KPIsState {
  viajes_completados: number;
  viajes_vacios_evitados: number;
  paradas_evitadas: number;
  tiempo_medio_entrega_min: number;
  km_evitados: number;
  roi_km_pct: number;
}

export interface SimulationSnapshot {
  sim_time: number;
  tick_id: number;
  amrs: AMRState[];
  lines: LineaState[];
  obstacles: ObstaculoState[];
  kpis: KPIsState;
}
```

---

## 2. Endpoints REST (FastAPI)

Todos los endpoints REST utilizan prefijo `/api/v1` (excepto `/health` y `/ws`).

| Método | Ruta | Descripción | Request Body | Response (200 OK) |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Healthcheck del backend y estado del engine | *Ninguno* | `{"status": "ok", "version": "1.0.0", "sim_running": true}` |
| `GET` | `/api/v1/plants` | Catálogo de plantas disponibles (Quito, Guayaquil) | *Ninguno* | `{"plants": [{"id": "quito", "nombre": "...", "layout_url": "..."}, ...]}` |
| `GET` | `/api/v1/layout` | Obtener el mapa de la planta (soporta query `?plant=quito` o `?plant=cd_guayaquil`) | *Query param opcional* | Objeto `PlantLayout` completo (`canvas`, `nodes`, `edges`, `pedestrians`) |
| `POST` | `/api/v1/sim/select` | Conmutar simulación en vivo a otra planta | `{"plant": "cd_guayaquil"}` | `{"status": "ok", "plant": "cd_guayaquil"}` |
| `GET` | `/api/v1/fleet` | Lista estática/detallada de la flota de AMRs | *Ninguno* | `[{"id": "AMR_01", "nombre": "...", "capacidad_kg": 500, ...}]` |
| `GET` | `/api/v1/missions` | Lista de misiones activas y en cola de despacho | *Ninguno* | `[{"id": "TSK_01", "tipo": "SUPPLY_REQUEST", "origen": "WH_MP_1", "destino": "E1_IN", "prioridad": 10, "estado": "pendiente"}]` |
| `GET` | `/api/v1/metrics` | Resumen acumulado de KPIs y métricas de ROI | *Ninguno* | Objeto `kpis` con histórico de viajes y tiempos |
| `POST` | `/api/v1/obstacles/block` | Bloquear dinámicamente un segmento/pasillo de la planta | `{"from": "X_02", "to": "X_05", "tipo": "SPILL"}` | `{"status": "blocked", "edge": ["X_02", "X_05"], "rerouted_amrs": ["AMR_01"]}` |
| `POST` | `/api/v1/obstacles/unblock` | Desbloquear un segmento/pasillo previamente inhabilitado | `{"from": "X_02", "to": "X_05"}` | `{"status": "unblocked", "edge": ["X_02", "X_05"]}` |
| `POST` | `/api/v1/sim/peak` | Inyectar pico de demanda instantáneo en una línea | `{"line_id": "E1_IN", "drain_pct": 30.0}` | `{"status": "peak_injected", "line_id": "E1_IN", "new_level_pct": 12.0}` |
| `POST` | `/api/v1/sim/low_battery` | Forzar batería 15% en un AMR y crear misión RECHARGE al cargador libre más cercano (occupancy-aware: elige entre CHARGER_1/CHARGER_2 por ocupación + distancia) | `{"amr_id": "AMR_01"}` | `{"status": "ok", "amr_id": "AMR_01", "target": "CHARGER_2"}` |
| `POST` | `/api/v1/sim/refill` | Fijar objetivo de insumos (default 80%) y encadenar SUPPLY_REQUEST por línea hasta alcanzarlo (cada entrega +20%, ~4 viajes por línea; omitiendo `line_id` aplica a todas las empacadoras) | `{"line_id": "E1_IN", "target_pct": 85}` / `{"target_pct": 80}` | `{"status": "refill_scheduled", "target_pct": 85.0, "line_id": "E1_IN", "lines": ["E1_IN", "E2_IN"]}` |
| `POST` | `/api/v1/sim/reset_missions` | Limpiar cola de misiones (útil para reset de demo) | *Ninguno* | `{"status": "ok", "missions_clearadas": 3, "activas": 0}` |
| `POST` | `/api/v1/sim/adjust_missions` | Sumar/restar misiones pendientes para mostrar cola reactiva | `{"delta": 5}` / `{"delta": -5}` | `{"status": "ok", "delta": 5, "pendientes": 8}` |
| `WS` | `/ws` | Canal bidireccional de telemetría continua | *Handshake WebSocket* | Stream de `SimulationSnapshot` a 5 Hz |

> **Uso en demo (Ronda 3):** El frontend invoca `POST /api/v1/sim/low_battery` desde el botón "Simular 15% batería" del panel de flota (`frontend/lib/api.ts:simulateLowBattery`) para mostrar en vivo el desvío a carga (`CHARGING`) y recuperación. Campo: `backend/app/models.py:LowBatteryRequest`, `backend/app/api.py:post_sim_low_battery`.

> **Ronda 5 (refill + batería viva):** `POST /api/v1/sim/refill` encadena entregas (cada una suma **20%** y se re-encola otra hasta cubrir el objetivo; ~4 viajes por línea para llegar a ≥80%). Además el backend **ya consume batería en tránsito** (`agents.py:_move_along_path`) y dispara **autocarga orgánica**: si un AMR cae a ≤15% se prioriza el cargador más cercano sin necesidad de botón (`env.py:_auto_recharge_check`). El comodín `Nestlé Runner` participa como refuerzo cuando el backlog crece. Noticias nuevas: `LOW_BATTERY` e `INFO` (refill activado).
> **Ronda 6 (cargadores occupancy-aware):** La selección de cargador para `RECHARGE`/`low_battery` ahora considera **ocupación + distancia real** (`env.py:trigger_low_battery` / `agents.py`): si un cargador está ocupado por otro AMR en `CHARGING`, el siguiente AMR se deriva al otro cargador libre más cercano, repartiendo la flota entre `CHARGER_1` y `CHARGER_2` en vez de amontonarla.

> **Ronda 5.2 (reset/adjust misiones):** `POST /api/v1/sim/reset_missions` limpia la cola (sin body → `{status, missions_clearadas, activas}`) y `POST /api/v1/sim/adjust_missions` suma/resta misiones pendientes (`{delta: +5|-5}` → `{status, delta, pendientes}`). Útiles en demo para mostrar la cola reactiva: botón ⟳ Reiniciar tareas y botones ＋5/−5 misiones.

---

## 3. Enumeraciones y Constantes

### 3.1 Estados de un AMR (`EstadoAMR`)
- `IDLE`: Disponible en espera de asignación.
- `MOVING_TO_PICKUP`: En tránsito hacia la estación de origen para recoger carga.
- `LOADING`: Proceso de carga en bahía (demora 3s simulados).
- `MOVING_TO_DELIVERY`: En tránsito hacia el destino con carga a bordo.
- `UNLOADING`: Proceso de descarga en bahía (demora 3s simulados).
- `WAITING_OBSTACLE`: Detenido temporalmente por presencia de peatón en radio de seguridad (< 2.5 m).
- `REROUTING`: Recalculando ruta $A^*$ tras bloqueo de pasillo.
- `CHARGING`: Batería baja (< 20%), recargando en estación.
- `ERROR`: Falla técnica simulada.

### 3.2 Tipos y Prioridades de Tarea (`TipoTarea`)
| Código | Prioridad | Descripción | Origen Típico | Destino Típico |
| :--- | :---: | :--- | :--- | :--- |
| `SUPPLY_REQUEST` | **10** (Crítica) | Suministro urgente de insumos a empacadora con buffer < 25% | `WH_MP_1` / `WH_MP_2` | `E1_IN` / `E2_IN` |
| `PICKUP_PT` | **5** (Normal) | Retiro de pallet completo de producto terminado en salida de línea | `L1_OUT` / `L2_OUT` | `WH_PT_1` / `WH_PT_2` |
| `RECHARGE` | **8** (Alta) | Misión automática de recarga si batería < 20% | Posición actual | `CHARGER_1` / `CHARGER_2` |
| `RELOCATION` | **2** (Baja) | Rebalanceo de insumos entre bahías de almacén | `WH_MP_1` | `WH_MP_2` |

### 3.3 Estados de Tarea (`EstadoTarea`)
- `pendiente`: En cola de despacho esperando AMR disponible.
- `asignada`: Asignada por método Húngaro a un AMR específico.
- `en_curso`: AMR transportando la carga.
- `completada`: Entregada en destino y registrada en Kardex.

### 3.4 Tipos de Nodo (`TipoNodo`)
- `linea`: Salida de producción de Producto Terminado (PT).
- `empacadora`: Entrada de insumos y materiales de empaque (MP).
- `almacen`: Bahías de almacenamiento central (MP / PT).
- `cruce`: Intersección de pasillos y vías de tránsito.
- `carga`: Estación de recarga de batería.

---

## 4. Sistema de Coordenadas y Convenciones del Layout

1. **Resolución del Canvas:** Base canónica de **800 px (ancho) × 500 px (alto)**.
2. **Origen:** `(0, 0)` se ubica en la esquina superior izquierda.
3. **Escala Espacial:** 10 px $pprox$ 1.0 metro de planta.
4. **Distribución Física:**
   - **X = 80:** Zona de Producción y Empaque (Líneas `L1_OUT`, `L2_OUT`, `E1_IN`, `E2_IN`).
   - **X = 240, 400, 560:** Pasillos y Cruces Centrales (`X_01` a `X_12`).
   - **X = 720:** Zona de Almacenes Centrales (`WH_PT_1`, `WH_PT_2`, `WH_MP_1`, `WH_MP_2`).
   - **Y = 40 (Superior):** Estaciones de Carga (`CHARGER_1`, `CHARGER_2`).
