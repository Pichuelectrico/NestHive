# Mejoras UI de Recorrido y Animación con Emojis — NestLink

> Roadmap visual para que cada AMR comunique su estado sin leer texto. Derivable 100% del snapshot (`amrs[].estado`, `amrs[].bateria`, `amrs[].tarea_asignada`/`path`, `missions[]`) — sin cambios de backend.

## Convención de emojis propuesta

| Estado derivado | Emoji | Condición (snapshot) |
|---|---|---|
| Lleva insumos (SUPPLY) | 📦 / 🥫 | `tarea_asignada` existe y misión tipo SUPPLY / destino empacadora |
| Lleva PT (PICKUP) | 🏭📦 | misión tipo PICKUP_PT |
| Vacío / retorno | 🚚 | sin tarea o en IDLE |
| Batería cargada >50% | 🔋 | `bateria > 50` |
| Batería media 26-50% | 🔋 (ámbar) | `26 ≤ bateria ≤ 50` |
| Batería baja ≤25% | 🪫 | `bateria ≤ 25` |
| En carga | ⚡ | `estado === "CHARGING"` |
| Esperando obstáculo | ⏸️ | `WAITING_OBSTACLE` |
| Reruteo | 🔄 | `REROUTING` |

## Propuestas

### 1) Etiqueta flotante con emoji de carga sobre cada AMR — (a) pre-evento · S
- **Qué:** Badge flotante encima del sprite del AMR en `PlantMap.tsx` con 📦/🏭📦/🚚 según lleva carga.
- **Aporta:** El jurado ve de un vistazo quién lleva producto vs quién va vacío (valor intralogística).
- **Archivo:** `frontend/components/PlantMap.tsx`

### 2) Emoji de batería en el propio AMR + FleetBatteryPanel — (a) pre-evento · S
- **Qué:** Superponer 🔋/🪫/⚡ junto al anillo de batería del AMR; en `FleetBatteryPanel.tsx` replicar emoji por fila.
- **Aporta:** Batería baja y carga se vuelven obvias sin leer %.
- **Archivo:** `PlantMap.tsx`, `FleetBatteryPanel.tsx`

### 3) Color/estela de ruta según tipo de carga — (a) pre-evento · M
- **Qué:** Línea de `path` en mapa con color: cian (vacío), ámbar (SUPPLY), violeta (PICKUP_PT); opcional estela/glow tras el AMR.
- **Aporta:** Diferencia visual de flujos PT vs insumos.
- **Archivo:** `PlantMap.tsx`

### 4) Anillo pulsante por prioridad de misión — (b) post-evento · M
- **Qué:** Anillo pulsante alrededor del AMR cuando su misión es P10 (crítica) vs P5 (normal).
- **Aporta:** Destaca urgencia sin saturar.
- **Archivo:** `PlantMap.tsx`

### 5) Línea de ruta animada (dash marching) según estado — (a) pre-evento · S
- **Qué:** Path con `stroke-dasharray` animado; velocidad del dash según `estado` (rápido MOVING, lento WAITING).
- **Aporta:** Movimento percibido incluso con tick 5 Hz.
- **Archivo:** `PlantMap.tsx`

### 6) Transición suave al cargar/descargar (scale + emoji) — (b) post-evento · S
- **Qué:** Al entrar en LOADING/UNLOADING, pequeño pop del emoji 📦 con `framer-motion`.
- **Aporta:** Feedback de manipulación de carga.
- **Archivo:** `PlantMap.tsx`

### 7) Tooltip/hover con detalle de misión + emoji — (b) post-evento · S
- **Qué:** Hover sobre AMR muestra `tarea_asignada`, tipo y destino con emoji.
- **Archivo:** `PlantMap.tsx`

## Priorización

| Prioridad | Mejoras |
|---|---|
| Pre-evento (hacer ya) | 1, 2, 3, 5 |
| Post-evento | 4, 6, 7 |

Top 3: **1 (etiqueta carga)**, **2 (emoji batería)**, **3 (color de ruta)** — máximo impacto con esfuerzo S/M y sin backend.
