# Banco Q&A Fase 2 · Jurado (10 min) — ⚠️ números v4 (28-oct)

> Preparación para el Q&A del pitch **NestHive** en Loja (28 oct). **Jurado: 2 de Nestlé Ecuador + 1 Cámara de Comercio de Quito + 1 U. de Alicante.** Formato: 5 min de pitch + **10 min de preguntas** ([[Bases Fase 2 (Loja)]]).
> Regla de oro: responder en 1–2 frases, remitir al apéndice y **nunca inventar un número** ([[KPIs y Procedencia]]).
> **Framing v5 (obligatorio):** hablamos SIEMPRE de la solución operando en la vida real. Flota = **4 AMRs MiR1350 (3 operativos + 1 backup), importados desde Colombia** — NUNCA decir "AGV" (AMR = navegación autónoma SLAM, sin obras civiles). Números canónicos: CAPEX **$0,64M** · ahorro **≈$0,27M/año** · payback **≈2,4 años — POR DEBAJO del estándar Nestlé (2,7–3, MÁX 3,5)** · labor real **$660×20 = $158,4k/año** · importación **CAN 0% + logística $20k** · IVA 15% ≈$96k **crédito fiscal recuperable** · 118 tests backend + 171/93 de mapa.

## 1 · "¿Esto es una simulación?" (la pregunta trampa #1)

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Esto es una simulación? | **Réplica anti-simulador:** "Lo que ven es el sistema operando — el mismo Néstor que, en el despliegue, se conecta al WCS de la planta. Cada cifra que les mostré sale de esa operación." | Guion oral §Q&A |
| ¿Los números son inventados? | No: cada KPI tiene fórmula y origen; el ahorro ≈$0,27M/año es un stack — labor real ($158,4k/año) + 45% km en vacío eliminados + energía por pallet + mermas — y la aritmética completa está en el deck. | [[KPIs y Procedencia]] |
| ¿Qué pasa cuando conecten datos reales? | El contrato REST/WS no cambia: la cola se alimenta del MES/WMS y Néstor pasa a reflejar la planta real; los 4 mensajes con SAP EWM ya están definidos. | [[Contrato API]] |

## 2 · Factibilidad

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Se integra con SAP/WMS? | Sí: 4 mensajes (PALLET_CLOSED, LABEL_VERIFIED, VDA order, VDA state) vía middleware PCo/CPI, con QoS 1 e idempotencia `orderUpdateId` — y el RFID del AMR actualiza SAP en la recogida, exactitud ≥99,9%. | [[NestLink · Evolución Fase 2]] |
| ¿Y si cae el Wi-Fi? | El AMR completa su misión con buffer local (VDA 5050), reintenta sincronización y la flota entra en modo degradado — la planta no para. | Capítulo Wi-Fi (deck) |
| ¿La "red Wi-Fi existente" les sirve? | Sí — el caso de negocio confirma Wi-Fi robusta + racks de posición fija: nuestra propuesta **no exige CAPEX de red**, solo roaming 802.11k/v/r y cobertura en pasillos de racks. | Capítulo Wi-Fi · [[Reto 2 Fase 2 · Gestión Inteligente de Inventarios]] |
| ¿Cuánto cuesta y cuándo paga? | CAPEX **$0,64M** — 4× MiR1350 con elevador de palets $440k + **importación desde Colombia: arancel 0% (CAN, Certificado de Origen) + logística y tasas $20k** + integración WCS + RFID + infra + puesta en marcha $180k; el **IVA 15% (~$96k) vuelve como crédito fiscal — no es costo**. Ahorro ≈**$0,27M/año**; **payback ≈2,4 años — POR DEBAJO del estándar Nestlé (2,7–3, máx 3,5)**. Y el pedido real: **piloto de 2 AMRs por $250k, reversible en <1 turno**. | [[Inversión y Retorno]] |

## 3 · Flota y operación

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Por qué 4 AMRs y no más? | Dimensionamiento por demanda: takt 132 s y 215 pallets/turno → **3 AMRs operativos cubren el pico con espera ≤30 s p95**; el 4º es **backup N+1 rotativo** para disponibilidad ≥98%. Ni un vehículo de más, ni uno de menos. | [[Asignación de Misiones]] |
| ¿Qué pasa si falla un AMR a mitad de misión? | Néstor lo saca del mapa y **re-rutea en vivo** — la planta no se detiene; si llevaba un pallet ya recogido, `abort_export` lo devuelve al buffer y reprograma; el backup entra rotando. | [[Asignación de Misiones]] |
| ¿AMR vs AGV — por qué AMR? | El AGV está esclavizado a una ruta física (cintas, imanes, cables → obras civiles); el **AMR navega de forma autónoma (SLAM)** — se implementa sin tocar el piso, re-rutea dinámicamente con Néstor y escala sin parar planta. Es la diferencia entre un tren y un conductor. | Deck slide Flota |
| ¿Por qué MiR y no ABB/Toyota? | **MiR** (Odense, Dinamarca) es el estándar de facto en AMRs con **representación y soporte en LatAm desde Colombia**, flota nativa **VDA 5050** y el **MiR1350** que carga 1.350 kg con elevador de palets — y con la importación CAN el arancel es 0%. ABB/Toyota quedan como alternativas evaluadas; el protocolo abierto de Néstor no ata la decisión. | Deck slide Flota |
| ¿El MiR1350 cuesta más de lo que dicen? | Cotización formal pendiente; el número es referencia de mercado. Incluso **con +30% por unidad, el payback sigue ≤3,2 años — dentro del estándar Nestlé**. | [[Inversión y Retorno]] |
| ¿Por qué importar desde Colombia y no directo de Dinamarca? | Tres razones: **arancel 0% por la Comunidad Andina** (Decisión 599, Certificado de Origen), **soporte técnico en español y huso horario compartido**, y repuestos con tránsito regional corto. Directo de Dinamarca aplicaría arancel de tercera país y soporte con vuelo europeo. | Deck slide Flota |
| ¿Cómo priorizan las misiones? | Cola única P1–P10 + asignación húngaro global con home-zones + rutas A* con reruteo dinámico; el kanban la hace visible en vivo. | [[Asignación de Misiones]] |
| ¿Escala a otro CD? | Otro centro = otro JSON de layout + grafo: **un centro, un mundo configurable**; el mismo Néstor opera todos desde un tablero. | [[Mapas de Planta]] |
| ¿Y si una línea cambia de producto/ritmo? | El takt (132 s) y los generadores son parámetros: reconfiguración sin re-diseño; el piloto valida contra el ritmo real. | [[Motor de Simulación]] |
| ¿La demanda crece — aguanta? | Con crecimiento del 5% anual, Néstor predice la saturación y planifica la siguiente inversión **antes del 85% de capacidad** (año 5: optimizar a 80% y extender vida útil). | Deck slide Escalabilidad |

## 4 · Seguridad

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Cómo conviven con personas? | AMRs con LiDAR 360° + zonas OSSD, estándar **ISO 3691-4 / IEC 61496 PLd Cat.3**; freeze ante peatones con timeout de 90 s que **respeta a la persona**. | [[Obstáculos y Evasión AMR]] |
| ¿Y los choques entre AMRs? | Protocolo de ceder el paso: `detect_head_on_pairs` + `pick_winner` (prioridad → distancia → id); 0 incidentes como KPI comprometido. | [[Obstáculos y Evasión AMR]] |

## 5 · Preguntas trampa (de quien conoce el producto)

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿El factor 0,32 km × 0,45 de dónde sale? | 0,32 km = viaje medio evitado (medido en planta); 0,45 = factor conservador para no sobrecontar viajes ya compartidos; ambos con rango de sensibilidad en el Anexo 4. | [[KPIs y Procedencia]] |
| ¿La evasión del MVP offline no está simplificada? | El MVP es la puerta de entrada ([[Modo Offline]]); la versión con backend completa incluye evasión head-on, ceder el paso y reruteo — **118 tests de backend + 171/93 de mapa en verde**. | [[Obstáculos y Evasión AMR]] |
| ¿Por qué no drones/RFID como el Reto 2? | Un dron **audita**, no mueve 1.035 pallets/día: el transporte físico es otro problema con otra solución — y NestHive además eleva la exactitud de inventario en tránsito a ≥99,9% con RFID. | [[Reto 1 Fase 2 · Transporte Interno]] |
| ¿El dashboard no es "maquillaje"? | El dashboard consume exactamente la API que usaría el WMS real; lo que se ve es el contrato completo de datos (fleet, misiones, KPIs), no una animación. | [[Contrato API]] · [[Dashboard Funcional]] |
| ¿Su referencia humana de 0,14 km/viaje es realista? | Es la referencia conservadora del Apéndice B; la sensibilidad está publicada y el payback se mantiene ≈3 años aun variando los supuestos — **dentro del estándar Nestlé (≤3,5)**. | [[Comparativa Humano vs NestLink]] |
| ¿Qué pasa si MiR no cumple la entrega? | El protocolo VDA 5050 de Néstor es abierto: ABB y Toyota (presentes en LatAm) ofrecen AMRs equivalentes sin re-escribir el software — el cambio de marca es configuración, no proyecto. | Deck slide Flota |

## 6 · PI y compromiso

| Pregunta | Respuesta corta | Remisión |
|---|---|---|
| ¿Entienden que la PI es de Nestlé? | Sí — 100% Nestlé Ecuador según las bases; el capital semilla se destina al desarrollo de la solución con Nestlé. | [[Bases Fase 2 (Loja)]] |
| ¿Qué necesitan de Nestlé para el piloto? | Acceso al layout y takt reales de la línea galletería, cuenta EWM de pruebas y 2 semanas de mapeo LiDAR — el cronograma de 5 fases ya lo detalla. | [[NestLink · Evolución Fase 2]] |

## Reglas del equipo para el Q&A

1. **Una frase, luego apéndice.** No monologar: el jurado quiere precisión, no discurso.
2. **Números solo del banco** ([[KPIs y Procedencia]]); si no está en el banco: "no lo medimos aún, y así lo mediríamos…".
3. **Si la pregunta es crítica**, agradecerla y responder con el rango, no el punto: los rangos son nuestra defensa.
4. **Jamás decir "simulador/simulación"** ante el jurado — si ellos lo mencionan, usar la réplica anti-simulador de §1.
5. Reparto: quien recibe la pregunta responde; Joshua respalda con demo; ESPOL con tecnología; UTPL con finanzas ([[Equipo Mixto Fase 2]]).
