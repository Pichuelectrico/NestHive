# Oral Pitch Fase 2 — Guion slide a slide (13 slides · 5:00 + Q&A 10 min)

> **Hackathon InnoLabs · Fase 2 · Loja · 27–28 oct 2026.** Equipo: Joshua (USFQ) + ESPOL + UTPL ([[Equipo Mixto Fase 2]]).
> Deck: `tasksR/pitch_deck/index.html` (13 slides). Q&A: banco completo en `tasksR/qa_jurado_fase2.md`.
> ⏱️ Objetivo: **4:55** (margen de 5 s). Ritmo: frases cortas. Cada bloque indica **quién habla**.

| Reparto | Voz en |
|---|---|
| **Joshua** | Apertura, problemática, demo, valor, cierre |
| **ESPOL** | Solución técnica, innovación, Wi-Fi, escalabilidad |
| **UTPL** | Inversión, sostenibilidad |

---

## Slide 1 · Portada (Joshua · 0:00–0:20)

**Qué se ve:** Logo NestHive + claim.
**Qué decimos:**
"Buenas. Somos el equipo NestHive: Joshua de la USFQ, y nuestros compañeros de ESPOL y UTPL. Hoy les mostramos cómo eliminamos el transporte manual entre producción y almacén con una flota de AMRs orquestada por software — y lo van a ver corriendo en vivo."

---

## Slide 2 · Eje 1 · Problemática (Joshua · 0:20–0:45) — fórmula Nestlé

**Qué se ve:** Doble flujo producción ↔ almacén + costos ocultos.
**Qué decimos — fórmula "necesidad → problema → efecto medible":**
"En Nestlé ocurre que 1.035 pallets deben moverse cada día entre producción y almacén sin frenar las líneas — porque ese flujo hoy depende de transporte y escaneo cien por ciento manuales, con un solo equipo por ruta como punto único de falla — lo que genera líneas que se detienen esperando insumo, sin trazabilidad digital, personas compartiendo pasillo con montacargas, y un costo oculto de doscientos mil dólares al año en la bodega."
*(Estructura: necesidad → problema → efecto. Una sola respiración por parte; señalar el diagrama en cada una.)*

---

## Slide 3 · Eje 2 · Solución + Viabilidad (ESPOL · 0:45–1:20)

**Qué se ve:** Arquitectura end-to-end + flota dimensionada + MiR1200 + transferencia.
**Qué decimos:**
"La solución es una flota coordinada por capas: percepción con LiDAR y visión, seguridad ISO 3691-4 con zonas OSSD, y un controlador de misión que decide qué robot, por dónde y cuándo. Dimensionado con matemática, no a ojo: ciclo de 146 a 158 segundos, pico de 1,4, techo de operación al 75% — dan seis MiR1200: cinco de línea y una reserva N+1. Y sin operarios tocando carga: el robot se acopla a la cinta a la misma altura, el pallet cae al robot y sale entregado."

---

## Slide 4 · Demo en vivo (Joshua · 1:20–2:00)

**Qué se ve:** Dashboard con planta realistic + KPIs en vivo.
**Qué decimos:**
"Esto no es un video: es la planta corriendo ahora. Miren: las líneas consumen insumos y la cola priorizada asigna cada misión al robot óptimo; aquí hay muros que ninguna ruta cruza — es diseño del grafo, no suerte. Disparo un pico de demanda… y la cola reordena sola por prioridad. Fuerzo batería baja… y el robot va solo a un cargador libre. Y el ciclo completo: producto a paletizado, los cuatro puntos de salida, y el AMR 6 — nuestro montacargas — por su ruta rosada exclusiva hasta el muro de entrega. Todo con KPIs subiendo en vivo."

---

## Slide 5 · Eje 3 · Innovación (ESPOL · 2:00–2:25)

**Qué se ve:** 4 cards: misión por nodo, robustez, réplica digital, ciberseguridad.
**Qué decimos:**
"Tres diferencias. Primero: control de estado por punto de entrega, no un WMS que reparte a ciegas. Segundo: robustez en operación real — si un robot debe cargar, termina la entrega y luego carga. Tercero: todo corre sobre una réplica digital auditable de la planta, con ciberseguridad y AMRs propios: sin cajas negras."

---

## Slide 6 · Wi-Fi industrial + edge (ESPOL · 2:25–2:55) ⭐ nuevo

**Qué se ve:** "No pedimos red nueva: usamos la Wi-Fi que Nestlé ya tiene" + 4 cards.
**Qué decimos:**
"Y la pregunta incómoda: ¿y la red? La respuesta corta: no pedimos red nueva — el caso de negocio confirma que Nestlé ya tiene Wi-Fi robusta, SAP/WMS activo y racks con posición fija. Lo que exigimos es roaming bien hecho: 802.11 k/v/r con handover de menos de 50 milisegundos. Si un punto se queda sin señal, el robot termina su misión con buffer local y el protocolo VDA 5050 — sin duplicar mensajes. Y si la caída es larga, modo degradado: la flota completa lo iniciado y SAP EWM reconcilia al volver. La misión nunca muere por red."

---

## Slide 7 · Eje 4 · Propuesta de valor (Joshua · 2:55–3:20)

**Qué se ve:** 4 cards de impacto medido + tagline "20 % de la calificación".
**Qué decimos:**
"El valor, medido con números que cada uno puede auditar en el apéndice: productividad — la flota nunca se detiene y los puntos de salida siempre están disponibles; seguridad — cero incidentes por diseño; y una réplica digital que se configura, no se reprograma: escalar a otra línea o a otro centro es cuestión de datos, no de desarrollo."

---

## Slide 8 · Inversión y retorno (UTPL · 3:20–3:50)

**Qué se ve:** CAPEX $0,95M · ahorro $0,21M/año · tarjeta roja del piloto $0,22M.
**Qué decimos:**
"El costo, con honestidad: la flota completa cuesta cerca de 950 mil dólares y ahorra unos 210 mil al año — payback de cuatro años y medio, menos de tres en tres turnos. Pero nosotros no pedimos un millón el día uno: pedimos un **piloto de dos robots por 220 mil dólares**, reversible en menos de un turno, medido contra el takt real de la línea. Si el piloto cumple — y el modelo dice que cumple — el despliegue completo se paga solo."

---

## Slide 9 · Eje 5 · Sostenibilidad (UTPL · 3:50–4:15)

**Qué se ve:** Net Zero + ODS 9 + aportes medibles.
**Qué decimos:**
"La eficiencia es sostenibilidad con números: menos kilómetros en vacío, menos energía por pallet, menos mermas por paradas. Alineado con el Net Zero 2050 de Nestlé y con el ODS 9 de las bases — industria, innovación e infraestructura. Más pallets con menos recursos: eso es sostenibilidad medible, no un eslogan."

---

## Slide 10 · Eje 6 · Escalabilidad (ESPOL · 4:15–4:35)

**Qué se ve:** Réplica de planta configurable (JSON + grafo) + multi-CD.
**Qué decimos:**
"¿Y escalar? Otra planta es otro archivo de layout y su grafo: ya operamos tres conmutables en caliente. El mismo contrato VDA 5050 y SAP EWM sirve para el siguiente centro — el software ya está probado; lo que se replica es configuración."

---

## Slide 11 · Cierre (Joshua · 4:35–4:55)

**Qué se ve:** URL del MVP + frase final.
**Qué decimos:**
"No les dejamos una promesa: les dejamos el producto funcionando. Pueden abrirlo ahora mismo desde su teléfono — mare1225.github.io/NestLink, el prototipo de fase 1 que hoy presentamos evolucionado como NestHive — un turno completo de la planta en setenta segundos, sin instalar nada. Somos NestHive: las líneas nunca esperan. Gracias."

---

## Q&A (10 min) — cómo operarlo

1. **Banco oficial:** `tasksR/qa_jurado_fase2.md` — 20+ preguntas con respuesta de 1–2 frases y remisión a apéndice.
2. **Regla:** responde quien recibe la pregunta; el resto respalda (Joshua=demo, ESPOL=tecnología, UTPL=finanzas). **Una frase, luego apéndice.**
3. **Números:** solo los del banco (los 10 del onboarding). Si no está: *"no lo medimos aún; así lo mediríamos…"*.
4. **Si la pregunta ataca supuestos** (el escenario Mare): responder con el **rango**, no el punto — el Anexo 4 publica sensibilidad ($0,13–0,30M de ahorro; payback ≤3 años en 3 turnos).
5. **Réplica anti-Reto-2 lista:** *"un dron audita; no mueve 1.035 pallets/día — el transporte físico es otro problema, y NestHive además eleva la exactitud de inventario a ≥99,9%."*

---

## Ensayo (checklist)

- [ ] Cronometrar los 11 bloques: total ≤ 4:55 (usar auto-avance del deck como metrónomo: 25 s/slide).
- [ ] Joshua: ensayar demo (planta realistic, pico, batería, AMR 6) — 40 s exactos.
- [ ] ESPOL: memorizar slide Wi-Fi (2:25–2:55) y réplicas técnicas.
- [ ] UTPL: memorizar piloto $0,22M + payback (3:20–3:50).
- [ ] Ensayar Q&A 10 min con el banco (rol de "jurado hostil" rotativo).
- [ ] Verificar URL en móvil con datos móviles (plan B, sin Wi-Fi del evento).

> 🔒 Todo el material queda en local — nada se sube a GitHub en fase 2.
