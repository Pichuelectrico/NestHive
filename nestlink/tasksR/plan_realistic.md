# 📋 Plan: mapa "realistic" (dibujado a mano) + nueva ronda de cambios

> Estado: **IMAGEN RECIBIDA (4-sep)** — port de realistic en curso.
> Se marca ✅ cada ítem al completarse. Este archivo es el coordinador de la ronda (lead: Aion CLI).

## 0) Cambios de fondo (ya autorizados, pueden arrancar ya)

- [x] **Branding Nestlé — Rojo + Blanco** (frontend · dueño: **Cursor**)
  - ✅ Hecho (commit 109f819): tema claro marca, rojo `#E4032E`, superficies blancas; PlantMap intacto, tsc EXIT 0.
- [x] **Eliminar planta "huge"** (backend/datos · dueño: **OpenCode**)
  - ✅ Hecho (commit 109f819): fuera de PLANT_CONFIGS, borrados huge.json/seed_huge/convert_huge, test_round10 ajustado, /plants sin huge, default quito, pytest 64/64.

## 1) Mapa "realistic" (lo que viene)

- [x] **Recibir la imagen del mapa dibujado a mano** (input del usuario)
  - ✅ Recibido 4-sep (2 archivos). Copiados al repo para trazabilidad en `backend/app/data/maps/reference/`:
    - `realistic_grafo_nodos.jpg` (1539×1150) — el mapa con el GRAFO dibujado en ROJO.
    - `realistic_presentacion.jpg` (1518×1149) — el mapa para la presentación.
- [x] **Portar el dibujo → layout JSON `realistic.json`** (backend/datos · dueño: **OpenCode**)
  - ✅ Hecho (commit 30fdd60, 4-sep): canvas 1000×600, 74 nodos, 90 aristas bi (180 dirigidas), 4 zonas etiquetadas, 1 línea (L1..L2, E1..E2) con buffer_nodes + zonas MP/Out, 3 peatones, registrado en PLANT_CONFIGS.
  - ⚠️ **Requisito de peatones del usuario cumplido:** PED_01 recorre el GRAFO ROJO de forma ALEATORIA (X_T02→X_T08→X_M04→X_R11→X_R15→X_T12); PED_02 camina ENTRE MATERIA PRIMA y PALETIZADO (WH_MP_2→X_R23→X_M06→WH_PT_1); PED_03 pasillo. Validado en vivo: 3 OPERATOR en snapshot, todos en movimiento.
- [x] **Registrar "realistic" en `PLANT_CONFIGS`** + `seed_realistic.json` (4 líneas SKU Nestlé, 5 AMRs con `home_zone` en cruces X_* — NO operativo, ver fix de waiting v2).
- [x] **Validación backend**: boot 180+ ticks sin errores, `select_plant("realistic")`, snapshot (5 AMRs + 3 peatones + 4 líneas), integridad de grafo (conectado, sin huérfanos), `pytest` suite completa **72/72 verde**.

## 2) Narrativa pitch: la ruta = LiDAR del AMR 🚚✨

> Concepto gancho del pitch: _"lo que ves trazado en el piso es el barrido LiDAR del AMR mapeando su entorno en tiempo real"_ → la ruta planificada se convierte en parte del storytelling de navegación autónoma.

- [x] **Ruta como sweep LiDAR** (frontend · dueño: **Cursor**)
  - ✅ Hecho (commit 46a605a, 4-sep): PlantMap sweep LiDAR (rastro glow cian + cono/spotlight en dirección de avance + rayo + dash animado por simTime determinista) + toggle 📡 "LiDAR" en ControlPanel (estilo marca, default ON al seleccionar realistic) + leyenda "LiDAR · SLAM run". tsc EXIT 0.
- [x] **AMRs del mismo color en Realistic** (frontend · dueño: **Cursor**)
  - ✅ Hecho (commit 46a605a, 4-sep): `getAmrColor(i, plantId)` → NESTLE_FLEET_RED #E4032E unificado si plantId==="realistic"; paleta por índice intacta en quito/guayaquil; aros de estado semánticos sin cambio.
- [ ] **Ajuste fino de animación**: sincronizar el sweep LiDAR con el LERP 60fps, sin romper estados/notices (verificación visual pendiente tras smoke test).

## 3) Cierre del demo (pitch 5 min)

- [x] **Flujo de negocio del paquete MP→Línea→Paletizado→Out** (backend · dueño: **Antigravity**)
  - Req usuario 4-sep: "los paquetes del momento en que entra materia prima a la linea de produccion, sale a paletizaje en 20segundos para este MVP, de Paletizaje a Out y de Out termina el recorrido". Estado: ✅ resuelto por Deep (2290d01) — ver abajo.
- [x] **Planta por defecto del arranque = "realistic"** (o la que el usuario elija) al levantar el stack Docker.
  - ✅ Hecho (commit cabeaa0, 4-sep): `sim_env` arranca en `DEFAULT_PLANT_ID="realistic"` (75 nodos); frontend `DEFAULT_PLANT_ID="realistic"` + fallback offline "Planta Realistic"; fallback local queda solo para Quito; tests api_integration/smoke fijan quito explícito. pytest 76/76, tsc EXIT 0, /health reporta plant=realistic.
- [x] **Mini-guion pitch 5 min cronometrado** (0:00–5:00 + 2 min Q&A): abrir con el problema Nestlé, demo en vivo de realistic (LiDAR + flota unificada), métricas ROI, cierre con sostenibilidad/escalabilidad. Preguntas difíciles y respuestas preparadas.
  - ✅ Hecho: `tasksR/pitch_5min.md` (guion 0:00–5:00 + 5 preguntas Q&A con respuestas).
- [x] **Smoke test final**: `docker compose up --build`, planta realistic, 1 min de sim sin errores, tsc EXIT 0.

---

- [x] **Flujo de negocio del paquete MP→Línea→Paletizado→Out** (backend · dueño: **Deep**)
  - ✅ Hecho (commit 2290d01, 4-sep): EXPEDITION (tipo aditivo), línea con acumulador 20 s genera PICKUP_PT Línea→WH_PT cada ~20 s con insumo; al entregar en Paletizado se encadena EXPEDITION WH_PT→OUT (fin del recorrido, sin misión posterior). pytest 76/76; en vivo realistics mostró 7 SUPPLY + 6 PICKUP_PT + 6 EXPEDITION a OUT.

**Checklist rápida de estado**

- [x] Branding rojo/blanco (109f819)
- [x] Huge eliminado (109f819)
- [x] Imagen realistic recibida (4-sep)
- [x] realistic.json portado + registrado + seed (30fdd60)
- [x] Ruta = LiDAR implementado (46a605a)
- [x] AMRs mismo color en realistic (46a605a)
- [x] Corrección layout realistic OUT/paredes/arista (5112bde)
- [x] Flujo de negocio del paquete MP→Línea→Paletizado→Out→fin (2290d01)
- [x] Default+pitch listo (default=cabeaa0 · pitch=pitch_5min.md)
- [x] Feedback ronda 2 (b5b377b): X_T11↔OUT (no X_M02), WH_MP_5→X_R25 solo, WH_PT_3→X_M05, y **muros VISIBLES** (bug "los muros no existen aun") — capa `walls` en realistic.json + render negro en PlantMap, sin cruzar aristas. pytest 76/76, tsc EXIT 0.
- [x] Feedback ronda 2.1 (c20a8af): B10/B20 + muros físicos + borde externo (detalle abajo).
- [x] Feedback ronda 2.2 (99e6be8 + b99d92e): **quitar B10/B20** (error: eran X_R10/X_R20) → X_T16→X_R10, X_T17→X_R20; **W1 corregido al OESTE de OUT** (472,64,8,240) — la x609 al este era errónea (lectura de archivo equivocado cuando falló la visión). Póster y anotación confirman: sin pared este. Layout final 75/92/6, pytest 79/79.
- [x] Feedback ronda 2.3 (9be1838): **W1/W2 alargados hasta pared externa sur (y=592)** + **BUG peatones atraviesan muros resuelto de raíz** (enrutados por grafo filtrado G vía nx.shortest_path + clamp defensivo). pytest 82/82, grafo 75/75 conexo (0 aristas perdidas).
- [x] Feedback ronda 2.4 (c5ad281): **nombres AMR → "AMR#"** (`seed_realistic.json` `nombre` = "AMR 1".."AMR 5", ids intactos) + PlantMap.tsx muestra nombre completo si empieza con "AMR " (evita colapsar los 5 a "AMR"). pytest 82/82, tsc 0, `/api/v1/fleet` → "AMR 1"…; layout 75/92/6. Sin cambios de muros post-demo aún (calibración Cursor pendiente de aplicar).
- [x] Feedback ronda 2.5 (`1f120ea`): **ruta rosada exclusiva OUT→muro**: 4 OUTs (OUT..OUT_4 en columna x=530) + corredor rosa hasta **MURO_ENTREGA** (530,576, pared inferior). AMR_06 "AMR 6" de entrega exclusiva (idle en el muro, solo mueve si hay stock). `out_stock` en snapshot → emoji 📦 sobre OUTs con paquete; EXPORT solo lo toma AMR_06; EXPEDITION balancea a mejor OUT; aristas `entrega:true` pintadas en rosa. Topología del usuario: sin OUT2↔OUT3, OUT3↔X_T12, OUT2↔MURO_ENTREGA directo. Layout live **81/99/6**, pytest 83/83, tsc 0.
- [x] Feedback ronda 2.6 (`01b0da6`): **OUT_3/OUT_4 a la derecha de OUT/OUT_2 (grid 2×2)** — delegado a Deep. OUT_3→(620,200), OUT_4→(620,290); P_OUT1/P_OUT2 borrados; aristas OUT↔OUT_3 y OUT_2↔OUT_4 (rosa); zona OUT ampliada. Layout **79/98/6** conexo; pytest 83/83 + sim 900 ticks (4 OUTs usados, 5 EXPORT→muro). Cursor confirma corredor vertical x≈549→pared SUR (refinamiento opcional post-demo).
- [x] Feedback ronda 2.7 (`b9abd83`): **mission control de estados/asignaciones OUT** — bug del usuario: dos AMRs dejaban un paquete en el OUT en el MISMO segundo y el AMR de entrega no lo contaba → paquete ocupando el OUT para siempre. Fix: `out_stock` (paquetes en buffer → 📦) + `out_en_ruta` (EXPORT provisionadas, contador explícito) en `env.py`; métodos `out_arrive`/`out_pickup`/`out_ship` reemplazan el escaneo de cola de misiones (fallaba con EXPORT en curso) → invariante: ambos drenan a 0 y el envío se encadena al siguiente paquete. `pick_best_out` balancea por (stock, en_ruta, pallets en tránsito al OUT, distancia, nombre). AMR_06 (entrega exclusiva) fuera de Hungarian pool y RELOCATION; EXPORT solo lo asigna a AMR_06. pytest **85/85** (test_06 = control directo: 2 llegadas mismo instante → se provisiona 1 EXPORT y drena todo; test_07 = integración del bug exacto: 2 AMRs mismo tick mismo OUT → AMR_06 drena ambos → 0 atrapados), tsc 0, en vivo OK.
- [x] Feedback ronda 2.8 (`de107c3`): **BUG AMR exclusivo olvida entregas mientras carga + KPI "tiempo en OUT"** —
  - **Bug:** al ir a recargar (`trigger_low_battery`) con EXPORT en vuelo se marcaba la misión `completada` sin liberar `out_en_ruta` → paquete (y futuros) atrapado en el OUT para siempre.
  - **Fix (env.py):** `abort_export()` enganchado en `trigger_low_battery` para EXPORT: si ya recogido (en_curso) **devuelve el paquete al buffer** (stock+1, reinicia reloj) ; libera slot y **reprograma** vía `_provision_export()` (nuevo punto único de creación de EXPORT compartido con out_arrive/out_ship). Invariante robusto: stock>0 ∧ en_ruta==0 ⇒ exactamente una EXPORT.
  - **KPI nuevo `tiempo_medio_en_out_min`:** FIFO `_out_pkg_arrivals[OUT]` (arribo) → `out_ship` cierra (sim_time−t0) → `KPIManager.record_out_wait_sec` → `KPIsState` → frontend (KpiBar + mini "En OUT (prom.)" violeta, types/demoEngine/EMPTY_KPIS).
  - **Validación:** pytest **89/89** (+4 en test_round14: aborto en vuelo → drena 0 colgadas; aborto tras recoger → vuelve a buffer; KPI arribo→ship; regresión "paquetes llegados durante carga → se entregan al volver"). tsc 0. E2E 1500 ticks con 35 recargas forzadas → 0 colgadas; natural 2500 ticks → 18 envíos, KPI 1.53 min, OUTs a 0. Rebuild api+web live OK.

- [x] **Ronda 2.2 (corrección conceptos) — cerrado (commits `99e6be8` + `b99d92e`, 4-sep):** el usuario aclaró que **no eran B10/B20 sino X_R10/X_R20** (docks reales del layout) → se eliminaron los nodos almacén B10/B20 y se conectó **X_T16→X_R10** y **X_T17→X_R20**. Además corrigió la pared: **W1 va al OESTE de OUT** (x=472, cara oeste, entre W2=440 y OUT=480), **no al este** (x609 estaba mal: lo puse yo leyendo el archivo equivocado). El póster `realistic_presentacion.jpg` (que el usuario volvió a enviar idéntico) muestra **solo dos trazos verticales de pared al oeste** — no hay pared este. Estado final: **75 nodos / 92 aristas / 6 muros** (W1, W2, W_TOP/BOTTOM/LEFT/RIGHT), conexo 75/75, grafo sin cruces, pytest 79/79, en vivo `/api/v1/layout?plant=realistic` = 75/92/6.

**Feedback ronda 2.1 — cerrado (commit `c20a8af`, 4-sep)**
- Nodos nuevos de almacén **B10**(760,470) ↔ `X_T16` y **B20**(800,470) ↔ `X_T17` (zona de docks, como indicó el usuario con la imagen).
- **Wall W1 movido a x=609** (este del patio OUT, 8×364) ajustando el recorrido interno.
- **Borde = paredes externas** del perímetro: `W_TOP` (0,0,1000,8), `W_BOTTOM` (0,592,1000,8), `W_LEFT` (0,0,8,600), `W_RIGHT` (992,0,8,600) — representan las paredes externas del layout original.
- **Muros FÍSICOS (bug "humanos atraviesan los muros" resuelto):** `build_plant_graph` en `data_maps.py` filtra toda arista cuyo segmento cruce un rect de `layout.walls` (intersección segmento↔rect con pad 0.5, incluye endpoint-inside). Ningún AMR (camina por aristas de G) ni peatón (misma base) puede atravesar una pared. Solo plantas con `walls`; quito/guayaquil intactos.
- Layout final realistic: **77 nodos / 92 aristas / 6 muros**, grafo conexo sin huérfanos.
- Test guard `test_walls.py`: ninguna pared cruza una arista del grafo; conteo de nodos dinámico (`len(layout["nodes"])`, no hardcode). **pytest 79/79**, `npx tsc --noEmit` EXIT 0, ciclo de misiones vivo (SUPPLY/PICKUP_PT/RELOCATION) con el stack rebuild.

## Check-puntos pendientes / posibles ajustes (demo day)
- [ ] Si el usuario reenvía el layout original ("te lo vuelvo a pasar?") → alinear con precisión las **paredes externas del borde** (por ahora W_TOP/BOTTOM/LEFT/RIGHT = perímetro de la imagen 1000×600) y afinar posición de W1 (472,64,8,240, oeste) / W2 (440,70,8,230) según la lectura calibrada de visión del póster (Cursor, en curso). Validar de nuevo 0 cruces con `test_walls.py` antes de commit.
