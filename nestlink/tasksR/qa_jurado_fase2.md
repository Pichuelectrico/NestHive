# Banco Q&A Fase 2 · Jurado (10 min)

> Preparación para el Q&A del pitch **NestHive** (antes NestLink) en Loja (27–28 oct). **Jurado: 2 de Nestlé Ecuador + 1 Cámara de Comercio de Quito + 1 U. de Alicante.** Formato: 5 min de pitch + **10 min de preguntas** ([[Bases Fase 2 (Loja)]]).
> Regla de oro: responder en 1–2 frases, remitir al apéndice y **nunca inventar un número** ([[KPIs y Procedencia]]).

## 1 · Simulación y datos

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Por qué simulación y no datos reales? | La simulación con **seed 42** hace la demo determinista y auditable; el mismo motor expone la API que conectaríamos a datos reales del WMS sin reescribir nada. | [[Motor de Simulación]] · [[Contrato API]] |
| ¿Los números de la demo son inventados? | No: cada KPI tiene fórmula y rango publicado (ahorro $0,13–0,30M/año, no un número único); los supuestos están en el Anexo 4 del deck. | [[KPIs y Procedencia]] · [[NestLink · Evolución Fase 2]] |
| ¿Qué pasa cuando conecten datos reales? | El contrato REST/WS no cambia: la cola se alimenta del MES/WMS y el tick engine pasa a reflejar la planta real; ya definimos los 4 mensajes con SAP EWM. | [[Contrato API]] |

## 2 · Factibilidad (el 20 % que nombran en la rúbrica)

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Se integra con SAP/WMS? | Sí: 4 mensajes (PALLET_CLOSED, LABEL_VERIFIED, VDA order, VDA state) vía middleware PCo/CPI, con QoS 1 e idempotencia `orderUpdateId`. | [[NestLink · Evolución Fase 2]] |
| ¿Y si cae el Wi-Fi? | El AMR completa su misión con buffer local (VDA 5050), reintenta sincronización y la flota entra en modo degradado — la planta no para. | Capítulo Wi-Fi (deck, slide Wi-Fi) |
| ¿La "red Wi-Fi existente" les sirve? | Sí — el caso de negocio confirma Wi-Fi robusta + racks de posición fija: nuestra propuesta **no exige CAPEX de red**, solo roaming 802.11k/v/r y cobertura en pasillos de racks. | Capítulo Wi-Fi · [[Reto 2 Fase 2 · Gestión Inteligente de Inventarios]] |
| ¿Cuánto cuesta y cuándo paga? | CAPEX $0,95M (rango 0,7–1,3M), ahorro $0,21M/año, **payback ≤3 años**; y el pedido real es el **piloto de 2 AMR por $0,22M**, reversible en <1 turno. | [[Inversión y Retorno]] |

## 3 · Flota y operación

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Por qué 6 AMRs y no más? | Dimensionamiento matemático: ciclo 146/158 s → 2,13 robots → ×1,4 pico → ÷0,75 techo = 3,98 → **5 de línea + 1 reserva N+1**; con la fórmula de Sakasegawa operamos a 53 % de utilización (13 s de espera vs 111 s al 85 %). | [[NestLink · Evolución Fase 2]] |
| ¿Qué pasa si falla un AMR a mitad de misión? | La reserva N+1 toma la cola; si el AMR llevaba un pallet ya recogido, `abort_export` lo devuelve al buffer y reprograma; la flota nunca queda idle. | [[Asignación de Misiones]] |
| ¿Cómo priorizan las misiones? | Cola única P1–P10 + asignación húngaro global con home-zones + rutas A* con reruteo dinámico; el kanban la hace visible en vivo. | [[Asignación de Misiones]] |
| ¿Escala a otro CD? | Otra planta = otro JSON de layout + grafo; ya operamos 3 plantas conmutables en caliente. | [[Mapas de Planta]] |
| ¿Y si una línea cambia de producto/ritmo? | El takt (132 s) y los generadores son parámetros: reconfiguración sin re-diseño; el piloto valida contra el ritmo real. | [[Motor de Simulación]] |

## 4 · Seguridad

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Cómo conviven con personas? | MiR1200 con LiDAR 360° + zonas OSSD, estándar **ISO 3691-4 / IEC 61496 PLd Cat.3**; en nuestra simulación, freeze ante peatones con timeout de 90 s que **respeta a la persona**. | [[Obstáculos y Evasión AMR]] |
| ¿Y los choques entre AMRs? | Protocolo de ceder el paso: `detect_head_on_pairs` + `pick_winner` (prioridad → distancia → id); 0 incidentes como KPI comprometido. | [[Obstáculos y Evasión AMR]] |

## 5 · Rivalidad interna (preguntas trampa de quien conoce el producto)

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿El factor 0,32 km × 0,45 de dónde sale? | 0,32 km = viaje medio evitado (medido en planta); 0,45 = factor conservador para no sobrecontar viajes ya compartidos; ambos con rango de sensibilidad en el Anexo 4. | [[KPIs y Procedencia]] |
| ¿La evasión del MVP offline no está simplificada? | El MVP publicado es la puerta de entrada ([[Modo Offline]]); la versión con backend completa incluye evasión head-on, ceder el paso y reruteo — y 89/89 tests. | [[Obstáculos y Evasión AMR]] |
| ¿Por qué no drones/RFID como el Reto 2? | Un dron **audita**, no mueve 1.035 pallets/día: el transporte físico es otro problema con otra solución — y NestHive además eleva la exactitud de inventario en tránsito a ≥99,9 %. | [[Reto 1 Fase 2 · Transporte Interno]] |
| ¿El dashboard no es "maquillaje" de la simulación? | El dashboard consume exactamente la API que usaría el WMS real; lo que se ve es el contrato completo de datos (fleet, misiones, KPIs), no una animación. | [[Contrato API]] · [[Dashboard Funcional]] |
| ¿Su montacargas humano de 0,14 km/viaje es realista? | Es la referencia conservadora del Apéndice B; incluso duplicándolo, el payback sigue <5 años — la sensibilidad está publicada. | [[Comparativa Humano vs NestLink]] |

## 6 · PI y compromiso

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Entienden que la PI es de Nestlé? | Sí — 100 % Nestlé Ecuador según las bases; el capital semilla se destina al desarrollo de la solución con Nestlé. | [[Bases Fase 2 (Loja)]] |
| ¿Qué necesitan de Nestlé para el piloto? | Acceso al layout y takt reales de la línea galletería, cuenta EWM de pruebas y 2 semanas de mapeo LiDAR — el cronograma de 5 fases ya lo detalla. | [[NestLink · Evolución Fase 2]] |

## Reglas del equipo para el Q&A

1. **Una frase, luego apéndice.** No monologar: el jurado quiere precisión, no discurso.
2. **Números solo del banco** ([[KPIs y Procedencia]]); si no está en el banco: "no lo medimos aún, y así lo mediríamos…".
3. **Si la pregunta es crítica**, agradecerla y responder con el rango, no el punto: los rangos son nuestra defensa.
4. Reparto: quien recibe la pregunta responde; Joshua respalda con demo; ESPOL con tecnología; UTPL con finanzas ([[Equipo Mixto Fase 2]]).
