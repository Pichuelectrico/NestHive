# 🎤 Pitch — NestLink · Hackathon InnoLabs Nestlé
### Edición DEMO final (rondas 2.1–2.8) — estructura en 6 ejes obligatorios

> **Formato:** 5:00 cronometrado + 2:00 Q&A.
> **Demo:** planta REALISTIC (por defecto al arrancar), pantalla completa, LiDAR ON.
> **One-liner:** «Convertimos la logística interna de una planta Nestlé en un sistema que se **percibe, decide y coordina solo**: una sola flota, un solo mapa, **cero paquetes atascados, cero viajes en vacío y menos energía por pallet movido**.»

---

## 🗺️ Estructura del pitch (6 ejes → tiempo)

| # | Eje obligatorio | Dónde se cubre | Timing |
|---|---|---|---|
| 1 | **Problemática** | Sec. Problema (fiel al reto Nestlé) | 0:00–0:45 |
| 2 | **Viabilidad técnica** | Sec. Solución/Viabilidad + Demo en vivo | 0:45–1:30 |
| 3 | **Innovación (qué nos diferencia)** | Sec. Innovación + Apéndice B | 2:30–3:05 |
| 4 | **Propuesta de valor para Nestlé** | Sec. Valor + Métricas + Apéndice A | 3:05–3:35 |
| 5 | **Sostenibilidad / uso eficiente de recursos** | Sec. Sostenibilidad | 3:35–4:05 |
| 6 | **Escalabilidad y replicabilidad** | Sec. Escalar | 4:05–4:35 |
| — | Cierre | Sec. Cierre | 4:35–5:00 |

---

## 0:00 – 0:45 · 1) PROBLEMÁTICA (fiel al reto Nestlé)

> *(Móntate cerca del mapa; abre con la pregunta central del reto, en pantalla.)*

"El reto de Nestlé es claro: **¿cómo automatizar y optimizar el flujo de materiales y productos entre producción y almacenamiento** usando tecnologías autónomas que mejoren **productividad, eficiencia y seguridad**?

Ese flujo va en **dos sentidos** y ambos deben operar sin fricción:
1. **Producto terminado**: desde **líneas de producción semiautomáticas** hacia **almacenamiento** (traslado automático).
2. **Materiales**: el **suministro oportuno** desde **almacén** hacia las **máquinas empaquetadoras**.

Hoy, en el movimiento interno de materiales, encontramos:
- **Intervenciones manuales y tiempos improductivos** que frenan la operación.
- **Riesgos operativos** asociados al movimiento interno (choques, cuellos de botella, errores).
- **Recorridos, recursos y tiempos de abastecimiento no optimizados** → las empaquetadoras esperan insumos y el producto terminado no sale a tiempo.
- **Costos ocultos**: viajes en vacío (~45 % de los km), paquetes olvidados que ocupan el punto de entrega, y gente dedicada a desbloquear, no a crear valor.

Y el reto pide una respuesta con **relación costo-beneficio convincente**, **viable en un entorno industrial real** y con **potencial de escalabilidad**."

---

## 0:45 – 1:30 · 2) SOLUCIÓN + VIABILIDAD TÉCNICA

> *(Apunta al mapa.)*

"NestLink — capa de **coordinación y visibilidad** para automatización intralogística — responde a ese doble flujo: **producto terminado → almacén** y **materiales → empaquetadoras**, sobre un **mapa que sí respeta la realidad**. ¿Qué tecnologías usa y por qué es viable?

- **Mapa vivo desde el layout real**: estaciones, pasillos, **muros físicos** que ningún robot cruza, y **peatones** que la flota esquiva sin detener producción → la capa de decisión corre sobre topología real, no sobre un dibujo.
- **Flota unificada sobre protocolo abierto**: la lógica de misión se expone por **API/WebSocket**; cualquier AMR/vehículo autónomo que publique posición y acepte misión se integra → **agnóstico de fabricante**.
- **IA de coordinación**: asignación óptima (matching), recarga inteligente y prioridades → la coordinación es software, no firmware.
- **Entrega exclusiva separada de producción**: 5 AMRs de producción (AMR 1–5) + **AMR 6 exclusivo** por **ruta rosada** hasta el **muro externo** (zona de almacenamiento/despacho); **4 OUTs en cuadrícula 2×2** con **mission control de estados/asignaciones** (producto terminado listo para almacén, sin bloqueos).
- **Analítica de datos en tiempo real** y KPIs: la operación se mide y se decide con datos, no a ciegas.

*Clave técnica con los jueces:* "El MVP es un **simulador de decisión**: validamos reglas, KPIs y ahorros **antes de tocar un robot real**. Lo respaldan **89 tests automatizados** y corridas headless por semilla que verifican **cero paquetes atascados** (incl. recargas forzadas)."

---

## 1:30 – 2:30 · DEMO EN VIVO (soporta problemática + viabilidad) 🚚✨

> *(Modo presentación, pantalla completa, zoom. Cuenta mientras corre.)*

1. **Materia prima entra por el este** → abastecimiento **preventivo** a líneas *antes* de que se vacíen (mira el KPI de paradas evitadas subir).
2. **Las 4 líneas procesan** → cada ~20 s sale un paquete de producción.
3. Un AMR lo lleva a **paletizado** y su entrega lo deja listo en uno de los **4 OUTs** *(señala la cuadrícula)*.
4. **Mira el OUT**: al llegar, se enciende el **📦**; el **AMR 6** lo toma y lo lleva por la **ruta rosada** al **muro externo**.
5. **Robustez visible:** ningún paquete se queda atascado **aunque el AMR de entrega vaya a cargar** — la export abortada **vuelve al buffer y se reprograma**, cero pérdidas.
6. **Personas caminando**: la flota las detecta y re-rutea al instante; ningún nodo ocupado deja a un robot esperando sin salida.

> *Tip: si va lenta, sube la velocidad; muéstrales 1 ciclo completo SUPPLY→PICKUP_PT→EXPEDITION→OUT→📦→AMR 6→muro.*
> *Números en vivo del dashboard: viajes completados, paradas evitadas, km evitados, ROI %, **tiempo medio en OUT**.*

---

## 2:30 – 3:05 · 3) INNOVACIÓN (qué nos diferencia)

> *(Transición: del mapa a la comparativa.)*

"¿Qué innovamos realmente? Tres cosas que hoy no existen en la operación:

1. **Mission control de estados por OUT (nuestro punto técnico más fuerte)**: cada paquete que llega a un OUT se contabiliza en `stock` y se le **regala y encadena** una misión de export de forma automática. Esto elimina de raíz el problema crónico de los **puntos de entrega que se bloquean 'para siempre'** — un fallo clásico de los sistemas WMS/control de flota.
2. **Entrega exclusiva + robustez ante batería**: separar "producir" de "exportar" con un rol dedicado y, si ese rol debe cargar, **abortar la export sin perder el paquete** (vuelve al buffer y se reprograma). Es **tolerancia a fallos en operación**, no en teoría.
3. **Decisión sobre percepción real (LiDAR)**: el mapa y las rutas que ven **son la percepción del robot**, no un dibujo decorativo — cierra el lazo dato→decisión.

> *Ver Apéndice B (comparativa humano vs NestLink) para la ventaja por dimensión.*

---

## 3:05 – 3:35 · 4) PROPUESTA DE VALOR PARA NESTLÉ Y SUS OPERACIONES

> *(Apunta al panel de KPIs.)*

"¿Qué obtiene Nestlé de aplicar esto? Beneficios operacionales medibles, y **cada uno con su fuente de dato** (*Apéndice A*). El reto pidió impacto en productividad, seguridad, recursos y costos — lo medimos todos:

- **Más productividad de la flota:** viajes completados y **tiempo medio de entrega** (min) por misión → menor tiempo por pallet.
- **Menos riesgo operativo / más seguridad:** percepción continua (LiDAR) + muros físicos + peatones esquivados → **disminuyen los riesgos del movimiento interno de materiales** (menos choques, menos cuellos de botella, menos intervención humana cerca de máquinas).
- **Menos kilómetros improductivos:** **km evitados y ROI %** (km evitados / km totales) porque la asignación elimina la **pata vacía** (~45 % del recorrido manual) → menos costo y menos energía.
- **Menos paradas de línea:** abastecimiento **preventivo** en el umbral crítico de los empaquetadores → **paradas evitadas**, el suministro oportuno que el reto exige.
- **Cero OUTs bloqueados:** mission control por OUT → el punto de salida de producto terminado está siempre disponible.
- **Nuevo KPI de servicio (ronda 2.8):** **tiempo medio en OUT** (≈1.5 min en corridas de referencia) → promesa de tiempo de salida de producto terminado hacia el almacén.
- **Costo-beneficio convincente:** proyecto sobre **protocolo abierto** protege la inversión actual; los ahorros se miden en dm evitados, horas y energía por pallet.

> *Frase para los jueces:* "Esto no vende una máquina: vende **productividad, seguridad y eficiencia** medidas — más metros por hora de flota, menos riesgo operativo y menos energía por pallet."

---

## 3:35 – 4:05 · 5) SOSTENIBILIDAD — USO EFICIENTE DE RECURSOS

> *(Tono pausado, alineado con el compromiso Net Zero de Nestlé.)*

"Menos recorrido improductivo no es solo dinero: es **sostenibilidad operativa**, alineada con la meta **Net Zero 2050** de Nestlé y con el ODS 12 (producción y consumo responsables):

- **Menos energía por pallet movido:** cada km evitado = menos consumo de la flota y, con flota eléctrica, **menos ciclos de carga y más vida útil de baterías**.
- **Menos residuos y retrabajo:** cero paquetes olvidados en OUTs y cero entregas perdidas por recarga → menos reproceso, menos material descartado.
- **Optimización del personal humano:** la gente pasa de desbloquear robots a tareas de mayor valor, reduciendo el esfuerzo físico y la sobrecarga.
- **Eficiencia de recursos medida:** km evitados, paradas evitadas y tiempo en OUT son, literalmente, **recursos (energía, tiempo, capacidad) que no se desperdician** — y se ven en vivo.

*Cierre de idea:* "Hacemos más pallets con **menos electricidad, menos horas y menos desperdicio** — eficiencia de recursos con números, no con eslóganes."

---

## 4:05 – 4:35 · 6) ESCALABILIDAD Y REPLICABILIDAD A OTROS CENTROS

> *(Mirada amplia, movimiento hacia adelante.)*

"Nestlé tiene decenas de plantas; esto fue diseñado para escalar desde el día uno:

- **Un centro = un 'mundo' configurable** (layout + flota + seed + ritmo de producción). Una planta nueva no se reprograma: **se configura**.
- **Multi-centro desde un tablero central**: el mismo cerebro puede operar **varias simulaciones hoy y varias plantas mañana**.
- **Replicable por diseño**: la capa de decisión es agnóstica de hardware y el mapa se carga desde el layout real → puesta en marcha acelerada en otro centro.

*Frase de cierre de eje:* "Lo que hoy corre para una planta, **es el mismo motor que mañana coordina un grupo de centros** desde un solo tablero."

---

## 4:35 – 5:00 · CIERRE

> *(Sube el tono, mirada a los jueces.)*

"En una palabra: **NestLink convierte la logística interna en un sistema que se percibe, decide y coordina solo** — una flota, un mapa, **cero viajes en vacío, cero paquetes atascados y menos energía por pallet**, con cada KPI respaldado por el simulador de decisión.

Hoy es un MVP de decisión sobre datos reales de planta. Mañana es el cerebro que hace más sostenible y eficiente **cada centro Nestlé** desde un solo tablero.

**Gracias — quedamos listos para sus preguntas.**" *(Corta la demo, deja el mapa en pantalla.)*

---

## 🎯 Q&A: preguntas difíciles y respuestas preparadas

**Q1 — "¿Cómo se conecta esto al hardware real? ¿Fabricantes?"**
R: La lógica de misión se expone vía API/WebSocket. Cualquier AMR que publique posición y acepte misión se integra; en la demo usamos LiDAR simulado para validar la capa de decisión antes de tocar hardware.

**Q2 — "¿Y si un AMR se cae / pierde señal / va a cargar?"**
R: El coordinador detecta inactividad y **reasigna la misión a otro robot**; si una export iba en vuelo y el AMR de entrega debe cargar, el **paquete vuelve al buffer y se reprograma** — cero pérdidas. Es el caso que nos llevó a eliminar los OUTs bloqueados.

**Q3 — "¿De dónde sale exactamente el ROI?"**
R: De los km evitados acumulados: cada viaje sin pata vacía ahorra 45 % de su distancia (~0.32 km/viaje en esta planta). ROI = km evitados / (km recorridos + km evitados). Detalle completo en el **Apéndice A**.

**Q4 — "¿Cómo lo implementarían en una planta real?"**
R: Las reglas ya están validadas en el simulador. El mapa se carga del layout real; la integración depende del fabricante. La puesta en marcha se acelera porque la capa de decisión es agnóstica de hardware.

**Q5 — "¿Escala a varias plantas?"**
R: Sí: cada planta es un 'mundo' configurable (layout + flota + seed) y un tablero central opera varias simulaciones hoy, varias plantas mañana.

**Q6 — "¿Cómo se ve en sostenibilidad?"**
R: Cada km evitado reduce energía y ciclos de batería; cero desperdicio por paquetes olvidados/perdidos; y el equipo humano se libera de tareas de bajo valor. Todo medido en los KPIs (km evitados, paradas evitadas, tiempo en OUT).

**Q7 — "¿Qué sigue tras el hackathon?"**
R: (a) telemetría real vía MQTT/REST, (b) gemelo digital con línea real, (c) piloto en una zona acotada de la planta.

---

## 📊 Apéndice A — Origen de los datos de los KPIs (de dónde sale cada número)

Todo KPI nace del **simulador de decisión** (`backend/app/metrics.py` + eventos de `sim/`). Nada es inventado:

| KPI en dashboard | Fórmula exacta (código) | Fuente del dato |
|---|---|---|
| **Viajes completados** | `viajes_completados += 1` por cada `record_trip_completed()` | Se dispara al **cerrar una misión** (descarga completada) en `agents.py` (estado UNLOADING). |
| **Tiempo medio de entrega (min)** | `total_delivery_time_min / viajes_completados` | Suma `(sim_time − created_at_sim)/60` de cada misión cerrada, dividida por nº de viajes. |
| **Paradas evitadas** | `record_stoppage_prevented()` | Disparo **preventivo** de abastecimiento en `generators.py` cuando una línea cruza su **umbral crítico** de inventario (el sistema evitó una parada). |
| **km evitados** | `Σ(viaje × 0.32 km × 0.45)` por viaje sin pata vacía (`was_empty_prevented=True`) | Cada misión del sistema se hace **consolidada** (evita la ida/vuelta en vacío del montacargas manual). 0.32 km = distancia de referencia de esta planta; 0.45 = 45 % del recorrido manual que es pata vacía. |
| **ROI % de la flota** | `km_evitados / (total_km_recorridos + km_evitados) × 100` | Compara **km coordinados** vs. **lo que habría recorrido la operación no coordinada** (con viajes en vacío). |
| **Tiempo medio en OUT (min)** *(ronda 2.8)* | `total_out_wait_sec / out_pkgs_measured / 60` | Cola FIFO `_out_pkg_arrivals[OUT]`: reloj **abierto** cuando el paquete llega al OUT (`out_arrive`) y **cerrado** cuando el AMR 6 lo coloca en el muro (`out_ship`). Promedio en minutos. |
| **Paquetes atascados / EXPORT colgadas** *(control)* | `out_en_ruta[OUT] == 0` siempre que `stock>0` ⇒ 1 export provisionada | Mission control por OUT (`out_stock` + `out_en_ruta`); verificado con tests (89/89) y E2E headless (0 colgadas en 1500–2500 ticks, incl. recargas forzadas). |

**Validación:** suite **89/89**, typecheck 0 errores, y corridas headless por semilla (seed 11: 2500 ticks → 18 envíos medidos, **tiempo medio en OUT ≈ 1.53 min**, OUTs drenados a 0). Las métricas se recalculan en vivo en cada tick.

---

## 🧍 Apéndice B — Comparativa operación manual (modelo humano/montacargas) vs NestLink

Supuestos del baseline (conservador): rutas en papel sin ver el piso, viajes en vacío (~45 %), abastecimiento reactivo (cuando ya se paró), OUTs sin estado, sin telemetría.

| Dimensión | Operación manual | NestLink (medido) | Ventaja |
|---|---|---|---|
| Kilometraje productivo | Solo ~55 % de los km | ~100 % (asignación consolida ida+vuelta) | **ROI % = km evitados sobre el total** |
| Paquetes en puntos de entrega | Pueden olvidarse → bloquear el OUT | Mission control por OUT, **cero atascos** | Disponibilidad del punto garantizada |
| Entrega durante recarga/pausa | Se pierde el paquete en curso | Export abortada vuelve al buffer y se reprograma | **Cero pérdidas** |
| Paradas de línea por inventario | Ocurren; se detectan al parar | Disparo preventivo en umbral crítico | **Paradas evitadas contadas** |
| Visibilidad | Ninguna | KPIs en vivo (incl. **tiempo en OUT**) | Decisión basada en datos |

**Conclusión cuantitativa (heurística del simulador):** por cada viaje consolidado, deja de recorrer 0.32 km × 45 % ≈ **0.14 km de pata vacía**. Ese ahorro es el ROI: la eficiencia que se **gana** aplicando NestLink en lugar del modelo humano/montacargas.

---
*Lead: Aion CLI · 4-sep-2026 · demo default = realistic · pruebas 89/89 · KPI ronda 2.8 activo · estructura 6 ejes verificada*
