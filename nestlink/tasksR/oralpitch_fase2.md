# Oral Pitch Fase 2 — Guion slide a slide (14 bloques · 5:00 + Q&A)

> **Hackathon InnoLabs · Fase 2 · Loja · 27–28 oct 2026.** Solución: **NestHive** operando el **Nestlé Warehouse**.
> **Equipo:** Joshua Reinoso (USFQ) · Andrea Verdezoto (ESPOL) · Andrés Fernandez (UTPL).
> **Deck:** `tasksR/pitch_slides/index.html` (13 slides + Gracias; tecla **N** = guion en pantalla). Q&A: banco en `tasksR/qa_jurado_fase2.md` (⚠️ pendiente barrido de números → ver §Q&A).
> **Framing (regla de oro):** hablamos SIEMPRE de la solución operando en la vida real — sin "simulador", sin alternativas descartadas, sin "6 unidades". Flota = **4 AGVs (3 operativos + 1 backup)**.
> ⏱️ Objetivo: **4:55**. Ritmo: frases cortas. Cada bloque indica quién habla.

| Reparto | Voz en |
|---|---|
| **Joshua** | Apertura, problemática, Néstor, demo, valor, cierre |
| **Andrea (ESPOL)** | Arquitectura WCS/WMS, demanda, flota, innovación, escalabilidad |
| **Andrés (UTPL)** | Criterios, gestión humana, inversión, sostenibilidad |

---

## 1 · Portada (Joshua · 0:00–0:12)

**Se ve:** logo NestHive grande + tagline + equipo.
**Decimos:** "Buenas tardes. Somos NestHive: Joshua Reinoso de la USFQ, Andrea Verdezoto de ESPOL y Andrés Fernandez de UTPL. Una sola flota, un solo cerebro, cero desperdicio. En cinco minutos les mostramos cómo opera nuestro centro."

## 2 · Problemática (Joshua · 0:12–0:45)

**Se ve:** foto almacén real + doble flujo + costo oculto.
**Decimos:** "Cada día, 1.035 pallets deben moverse entre producción y el Nestlé Warehouse sin detener las líneas. Ese flujo hoy es manual: transporte y escaneo a mano, un solo equipo por ruta como punto único de falla. El efecto: líneas esperando insumo, inventario sin trazabilidad digital, personas compartiendo pasillo con montacargas — y casi la mitad de los kilómetros recorridos son pata vacía: puro costo oculto."

## 3 · NestHive + Néstor, la reina abeja (Joshua · 0:45–1:10)

**Se ve:** colmena — obreras AGVs, reina Néstor.
**Decimos:** "Nuestra solución tiene nombre: **Néstor**, la inteligencia orquestadora — la reina abeja de la colmena. Néstor gestiona los hilos de toda la operación: decide qué ruta usa cada vehículo, qué AGV atiende cada demanda, y reordena la colmena cuando algo cambia. Informa los datos en vivo y permite preguntarle rápido: *¿qué AGV está en transporte?* — y responde. Las obreras — los AGVs — solo ejecutan lo que la reina decide, y nunca van vacíos: cada movimiento está justificado por consumo real de línea."

## 4 · Arquitectura: WCS ⇄ Néstor ⇄ WMS/SAP (Andrea · 1:10–1:40)

**Se ve:** diagrama de 3 cajas + anillo RFID.
**Decimos:** "Néstor vive en el medio del ecosistema Nestlé. Abajo, el **WCS** ejecuta en piso: cintas, sensores y AGVs con la misión asignada. Arriba, el **WMS/SAP** dueño del inventario. Néstor conecta los dos: convierte la demanda en misiones, las asigna al AGV óptimo, y cierra el círculo con **RFID** — cuando un AGV recoge un palet, su lector escanea el tag y **actualiza SAP/WMS en tiempo real**. Inventario con exactitud de 99,9%, sin escaneo manual."

## 5 · Estrategia de movimiento de la demanda (Andrea · 1:40–2:00)

**Se ve:** takt + techo + curva predictiva.
**Decimos:** "Y no reaccionamos: anticipamos. Con el takt de la línea — 132 segundos — Néstor predice la demanda y mueve material **antes** de que la línea pida. Los sensores marcan el palet listo, Néstor lo detecta, y despacha. Esa estrategia nos da un techo de **411 pallets por turno — 91% más de capacidad** — sin saturar la entrada: crecimiento conservador del 5% anual, y Néstor calcula la saturación de la línea para planificar la siguiente inversión **antes** de necesitarla."

## 6 · Flota: 4 AGVs, 3 + 1 backup (Andrea · 2:00–2:20)

**Se ve:** foto AGV + robustez de averías.
**Decimos:** "La flota es deliberadamente pequeña: **cuatro AGVs — tres operativos y uno de backup**. Menos inversión, menos mantenimiento, misma cobertura. Y si uno se avería: se detiene, bloquea su tramo, los demás re-rutean solos, y si no hay paso, la operación pausa ordenada. Reparación en 10 segundos de operación y el backup asume sin perder misiones. Marcas probadas en Latinoamérica: MiR, ABB, Toyota — con soporte local."

## 7 · Demo en vivo — NestHive operando (Joshua · 2:20–2:50)

**Se ve:** pantalla con el Nestlé Warehouse corriendo: mapa, AGVs, Néstor informando, señales 🧩/📦.
**Decimos:** "Esto que ven es **NestHive operando el Nestlé Warehouse ahora mismo**. Las líneas consumen insumos — señales 🧩 — Néstor asigna cada AGV, el paletizado recibe 📦, y el flujo llega hasta Transporte sin que nadie empuje un botón. Miren los muros: ninguna ruta los cruza — es diseño del grafo, no suerte. Y cuando fuerza una avería… el tramo se bloquea, la flota re-rutea, la operación sigue. Todo con datos en vivo."

## 8 · Innovación (Joshua · 2:50–3:10)

**Se ve:** 4 cards: mission control, percepción real, Néstor conversacional, protocolo abierto.
**Decimos:** "Tres diferencias frente a un WMS tradicional: primero, **control de estado por punto** — Néstor decide con la percepción real de la planta, no a ciegas. Segundo, **mission control**: cero puntos bloqueados, cero paquetes olvidados. Y tercero, **Néstor conversacional**: el gerente pregunta, Néstor responde con datos. Todo sobre protocolo abierto — sin cajas negras. Trabajamos como pide Nestlé: velocidad sobre perfección, coraje sobre comodidad, colaboración sobre consenso."

## 9 · Por qué cumplimos sus criterios (Andrés · 3:10–3:35)

**Se ve:** tabla 6 criterios → evidencia.
**Decimos:** "Sobre los criterios de evaluación, punto por punto: **Innovación** — Néstor, la IA orquestadora que decide sobre percepción real. **Propuesta de valor** — techo de 411 pallets por turno: 91% más capacidad con la misma planta. **Efectividad** — 1.035 movimientos diarios con espera máxima de 30 segundos y averías que no detienen la planta. **Sustentabilidad** — Net Zero 2050, menos energía por pallet. **Escalabilidad** — crecimiento del 5% anual planificado por Néstor. Y **Replicabilidad** — otro centro es otro archivo de configuración, el mismo Néstor."

## 10 · Gestión del cambio humano (Andrés · 3:35–3:55)

**Se ve:** transición respetuosa — personas primero.
**Decimos:** "Y la parte que más pesa: las personas. El equipo de bodega son 20 colaboradores, y la automatización se aborda como Nestlé sabe hacerlo: **jubilaciones voluntarias** — con la edad promedio de 45 a 60 años —, **capacitación para emprendimientos**, acompañamiento familiar y psicológico, y **transferencia de conocimiento bidireccional**: el know-how operativo de los veteranos hacia el sistema, y lo digital de los jóvenes hacia la operación. Proceso transparente, sin conflicto — como el caso de Nestlé con 51 personas."

## 11 · Inversión y recuperación (Andrés · 3:55–4:20)

**Se ve:** tabla CAPEX + curva de ahorro cruzando el payback.
**Decimos:** "La inversión: **760 mil dólares** — cuatro AGVs, integración WCS, lectores RFID, infraestructura, aranceles de importación y puesta en marcha. ¿Y cómo se recupera? El ahorro anual llega a **más de 250 mil dólares**: la flota asume el transporte interno y los 20 colaboradores se reasignan a valor, más los kilómetros en vacío eliminados, la energía por pallet y las mermas. Resultado: **payback de menos de 3 años — dentro del estándar de Nestlé, que fija el máximo en 3,5**. Y si prefieren entrar por pasos: piloto de dos AGVs, reversible en menos de un turno."

## 12 · Sostenibilidad (Andrés · 4:20–4:35)

**Se ve:** Net Zero 2050 + ODS 12 + calidad del producto.
**Decimos:** "La eficiencia es sostenibilidad con números: menos kilómetros en vacío, menos energía por pallet, menos mermas — alineado con el **Net Zero 2050** y el **ODS 12**. Y la calidad también: control de temperatura y humedad en producción y empaque — porque el empaque es la barrera que protege la galleta. Más producto protegido con menos recursos."

## 13 · Escalabilidad y replicabilidad (Joshua · 4:35–4:50)

**Se ve:** multi-centro desde un tablero + misma Néstor.
**Decimos:** "¿Y mañana? Otro centro de distribución es otro archivo de configuración: Néstor predice la saturación, planifica la siguiente inversión y el mismo motor opera todos los centros desde un solo tablero. Lo que se replica es configuración — el cerebro ya está construido."

## 14 · Gracias (Joshua · 4:50–4:55)

**Se ve:** logo + "Gracias".
**Decimos:** "Somos NestHive. Las líneas nunca esperan. Muchas gracias."

---

## Q&A (10 min) — cómo operarlo

1. **Banco:** `tasksR/qa_jurado_fase2.md` — ⚠️ **pendiente: barrido de números a la versión nueva** (6 AMRs → 4 AGVs; payback 4,5 → ≈2,9; CAPEX 0,95 → 0,76 con arancel 75%; sin "AMR 6").
2. **Regla:** responde quien recibe la pregunta; el resto respalda (Joshua=demo/Néstor, Andrea=tecnología, Andrés=finanzas/personas). **Una frase, luego el dato del deck.**
3. **Números canónicos (los de la versión final):** 1.035 mov/día · 215/131 por turno · takt 132 s · techo 411 (+91%) · 4 AGVs (3+1) · CAPEX $0,76M (arancel 75% incluido) · ahorro $0,26–0,28M/año · **payback ≈2,9 años (estándar Nestlé: 2,7–3, máx 3,5)** · exactitud ≥99,9% (RFID) · disponibilidad ≥98% · espera ≤30 s p95 · 118+171 (+93 subtests) pruebas de plataforma.
4. **Si preguntan por el piloto:** 2 AGVs, reversible en menos de un turno, medido contra el takt real.
5. **Si preguntan por personas/huelgas:** proceso transparente + jubilaciones voluntarias + reasignación a valor; caso Nestlé 51 personas sin conflicto; riesgo sindical evaluado con el Business Partner.
6. **Si preguntan por Wi-Fi/red:** 802.11 k/v/r, handover <50 ms, buffer local + VDA 5050; Nestlé ya tiene la red — no pedimos una nueva.
7. **Si preguntan por el simulador/MVP:** el sistema opera en vivo sobre el modelo del centro; la integración WCS/RFID es el diseño de despliegue — *decirlo sin decir "simulador"*: "lo que ven es el sistema operando; el despliegue conecta el mismo Néstor al WCS de la planta".
8. **Réplica anti-Reto-2:** "un dron audita; no mueve 1.035 pallets/día — el transporte físico es otro problema, y NestHive además eleva la exactitud de inventario a ≥99,9% con RFID".

---

## Ensayo (checklist)

- [ ] Cronometrar los 14 bloques: total ≤ 4:55 (timings por slide en el deck; tecla N = guion en pantalla como teleprompter).
- [ ] Joshua: portada, problemática, Néstor, **demo 30 s exactos** (NestHive corriendo a pantalla completa en localhost), innovación, escalabilidad, cierre.
- [ ] Andrea: arquitectura WCS/WMS + RFID (memorizar la frase de SAP en tiempo real), demanda, flota con avería.
- [ ] Andrés: **criterios 6 en 25 s**, gestión humana, inversión con payback ≈2,9 "dentro del estándar Nestlé".
- [ ] Q&A 10 min con el banco (jurado hostil rotativo) tras actualizar los números (ver §Q&A).
- [ ] Plan B demo: deck completo sin demo en vivo (las 4 imágenes del deck + KPIs impresos en one-pager).

> 🔒 Material local — nada se sube a GitHub público.
