# Onboarding Exprés · Equipo Loja (ESPOL + UTPL)

> Tu entrada rápida al proyecto **NestHive** (antes NestLink) para la fase 2 del Hackathon InnoLabs (27–28 oct, UTPL Loja). Léelo en 10 minutos. Material completo: vault Obsidian `NestLink/Obsidian/Neslink/` → carpeta **06 Fase 2 · Loja**.

## 1 · Qué es NestHive (5 líneas)

1. **Tagline:** *"El Waze + cerebro de Nestlé para que sus AMRs nunca vayan vacíos y sus líneas nuncaparen."*
2. Es un **orquestador de flota** (software): escucha a las líneas, arma una **cola priorizada P1–P10**, asigna cada misión al AMR óptimo (algoritmo húngaro) y les calcula rutas (A*).
3. Tiene un **MVP funcionando en vivo**: https://mare1225.github.io/NestLink/ (abre y funciona, sin backend — modo offline).
4. Ganó el **Reto 1 en la fase 1 (Quito)** y ahora compite en Loja contra **otros 3 equipos mixtos** — uno de ellos liderado por alguien que conoce el producto por dentro: hay que estar afilados.
5. La propuesta fase 2 añade la **ingeniería de detalle**: celdas EOL, buffers, VDA 5050 + SAP EWM, dimensionamiento matemático de flota y plan de piloto.

## 2 · Los 4 dolores (el "antes")

1. **Bloqueo de línea** cuando falta insumo en el punto de uso.
2. **Punto único de falla**: 1 equipo, 2 flujos, 3 turnos.
3. **Trazabilidad manual**: 1.035 escaneos/día.
4. **Seguridad**: montacargas y personas compartiendo pasillo.

## 3 · Los 5 puntos técnicos (una frase cada uno)

| # | Tema | En una frase |
|---|---|---|
| 1 | **Asignación** | Cola priorizada P1–P10 + algoritmo húngaro con home-zones + rutas A* con reruteo dinámico |
| 2 | **Evasión** | Los AMRs ceden el paso entre sí (head-on) y ante peatones/derrames con freeze de 90 s que respeta a la persona |
| 3 | **Batería** | Drenaje continuo al moverse; autocarga ≤15 % con cargadores "occupancy-aware" (nunca dos AMRs al mismo cargador) |
| 4 | **Integración** | Fleet manager con protocolo **VDA 5050** (MQTT) + **SAP EWM** (4 mensajes, middleware PCo/CPI, buffer local si cae el Wi-Fi) |
| 5 | **Demo** | Dashboard en vivo: mapa, kanban, KPIs, batería; planta "realistic" con muros, ruta rosada y 4 OUTs |

## 4 · Los 10 números que hay que saber de memoria

| # | Número | Significado |
|---|---|---|
| 1 | **1.035** | Movimientos de pallets por día en la planta |
| 2 | **215 / 131** | Pallets de salida / entrada por turno |
| 3 | **132 s** | Takt (ritmo de la línea) |
| 4 | **6 AMRs** | Flota: 5 de línea + 1 reserva (N+1), MiR1200 |
| 5 | **89/89** | Tests del backend que pasan |
| 6 | **411 (+91 %)** | Techo de capacidad: pallets por turno con la flota completa |
| 7 | **$0,95M** | CAPEX total (rango 0,7–1,3M) |
| 8 | **$0,21M/año** | Ahorro anual (rango 0,13–0,30M) |
| 9 | **≤3 años** | Payback |
| 10 | **$0,22M** | **El pedido real: piloto de 2 AMR, reversible en <1 turno** |

> Bonus: exactitud de inventario **≥99,9 %**, disponibilidad **≥98 %**, espera por pallet **≤30 s (p95)**, incidentes **0**.

## 5 · Roles sugeridos en escena (validaremos el día 1)

| Momento | Quién | Qué |
|---|---|---|
| Problemática + demo | **Joshua** | Conoce el producto a fondo; maneja la demo en vivo |
| Tecnología + Wi-Fi + seguridad | **ESPOL** | Explica húngaro/A*, VDA 5050/EWM, el capítulo Wi-Fi y ISO 3691-4 |
| ROI, payback, cronograma, ODS 9 | **UTPL** | Lidera la sesión 5 del día 2 (inversión) y las respuestas financieras |
| Q&A (10 min) | Los 3 | Banco de respuestas: `tasksR/qa_jurado_fase2.md` |

## 6 · Agenda del evento (resumen)

| Día | Claves |
|---|---|
| **27 oct (aula 113, edificio 10)** | 8:30 bienvenida + retos por Nestlé · sesiones: problemática → propuesta de valor → prototipado, con 2 mentorías |
| **28 oct** | 8:30 ROI/payback/cronograma + mentoría · 11:00 pitch prep · **15:00–16:30 exposición al jurado** · 16:30 premiación |

## 7 · Cómo practicar antes del 27

1. Abre la demo: https://mare1225.github.io/NestLink/ — selecciona la planta **realistic**, pon un pico de demanda y mira cómo reordena la cola.
2. Lee en Obsidian: `00 Índice NestLink` → `NestLink` → `NestLink · Evolución Fase 2` → `Plan de Mejoras Fase 2`.
3. Memoriza la tabla de 10 números (§4) — es el 80 % del Q&A.
4. Lee `tasksR/qa_jurado_fase2.md` completo y ensaya tus respuestas en voz alta.

> 🔒 Regla de trabajo: **todo queda en local** — nada se sube a GitHub en esta fase.
