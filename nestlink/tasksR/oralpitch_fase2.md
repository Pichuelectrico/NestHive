# 🎤 Pitch oral Fase 2 — NestHive (v6 · deck morph KUKA)

> **Deck:** `Slides_pitch/pitch_morph.html` (16 slides, morph animations; tecla **N** = guion en pantalla). Copia del guion en `Slides_pitch/oralpitch_fase2.md`.
> **Framing (regla de oro):** hablamos SIEMPRE de la solución operando en la vida real — sin "simulador", sin alternativas descartadas. Flota = **4 AMRs KUKA KMP 600P (3 operativos + 1 backup), importados desde Colombia — arancel 0% CAN**. Nunca "AGV" ni "MiR".
> **Frase estrella (usar 2×):** "La infraestructura habla con Néstor y Néstor habla contigo."
> ⏱️ Objetivo: **5:00** (contenido hasta ~4:52; "Gracias" cierra). Tecla N = teleprompter.

| Reparto | Voz en |
|---|---|
| **Joshua** | Portada, problemática, Néstor, demo, flota KUKA, escalabilidad, cierre |
| **Andrea (ESPOL)** | PLC/asignación, **algoritmo húngaro**, mantenimiento, WMS/demanda |
| **Andrés (UTPL)** | Cifras de impacto, criterios 6/6, gestión humana, ROI + CAPEX |

## 1 · Portada (Joshua · 0:00–0:12)

**Se ve:** logo grande (morph).
**Decimos:** "Buenos días. Somos NestHive — y venimos a convertir el manejo de materiales de Nestlé Ecuador en su ventaja competitiva."

## 2 · Problemática — la cita que pesa (Joshua · 0:12–0:40)

**Se ve:** cita Tompkins + 4 dolores (morph).
**Decimos:** "James Tompkins, la referencia mundial en manejo de materiales, es claro: **entre el 20 y el 50% de los gastos operativos de una planta son mover material**. Cada pallet que espera ser retirado es capacidad de producción, espacio y tiempo que no se aprovechan. Nestlé Ecuador necesita **215 pallets de salida por turno — 645 al día solo de salida** — más todo el flujo de insumos: más de **1.000 movimientos diarios** que hoy cargan sobre montacargas, escaneos manuales y suerte."

## 3 · Néstor: el corazón + la frase (Joshua · 0:40–1:00)

**Se ve:** Néstor en el centro, conectando todo (morph).
**Decimos:** "El corazón de nuestro proyecto es **Néstor** — la reina abeja que orquesta la colmena. Néstor se comunica con los sistemas que ya existen en la planta y se comunica con el gerente. Nuestra promesa en una frase: **la infraestructura habla con Néstor, y Néstor habla contigo** — le preguntas qué AMR está en transporte, cuánto demorará la siguiente misión, y te responde con datos en segundos."

## 4 · Recepción de solicitudes: PLC → misión (Andrea · 1:00–1:18)

**Se ve:** pantalla de recepción de solicitudes (Canva p8) con cola P1–P10.
**Decimos:** "Todo empieza en el paletizado: el **PLC de la línea** — la señal 🧩 — avisa que el insumo se está consumiendo. Esa solicitud entra a Néstor, se convierte en misión con prioridad, y la asignación sale sola — **por prioridad y por disponibilidad**. Sin llamadas de radio, sin planillas, sin puntos ciegos."

## 5 · ⭐ Cómo orquesta Néstor: el algoritmo húngaro (Andrea · 1:18–1:44)

**Se ve:** matriz 4×4 armándose celda por celda (morph) → asignación óptima resaltada.
**Decimos:** "¿Y cómo decide qué AMR atiende qué misión? Con matemática elegante: el **algoritmo húngaro**. Cada misión pendiente y cada AMR libre forman una **matriz de costos**. Cada celda combina cinco datos: la **distancia estimada de ruta** — que Néstor calcula con A* —, la **prioridad de la misión, de P1 a P10**, el **nivel de batería** del AMR, su **estado** — libre o cargando — y su **home-zone**. El algoritmo húngaro resuelve esa matriz y encuentra la asignación de **costo mínimo global** — el mejor conjunto para TODA la planta, no el vehículo más cercano para cada misión. Y lo hace en milisegundos. **Greedy elige el más cercano; húngaro elige lo mejor para todos.**"

## 6 · Mantenimiento de flota + robustez (Andrea · 1:44–2:00)

**Se ve:** panel de mantenimiento (uptime, km, baterías, próx. servicio).
**Decimos:** "Y la colmena se cuida sola. Del software de cada AMR recibimos **tiempo de actividad, kilometraje, desgaste de baterías y fallas mecánicas** — Néstor avisa cuánto falta para el próximo mantenimiento y detecta la avería antes de que pare la planta. Si un AMR falla en plena misión: se bloquea su tramo, los demás **re-rutean solos y la producción sigue** — el backup asume. Disponibilidad ≥98%."

## 7 · WMS: demanda anticipada + RFID→SAP (Andrea · 2:00–2:18)

**Se ve:** alerta de insumos + flujo RFID (morph).
**Decimos:** "La productividad no se limita a los AMRs. Néstor también vigila el warehouse: con el **análisis promedio de uso por turno**, anticipa cuándo las cintas y empaques se van a acabar y **alerta al gerente antes** de que la línea espere. Y cada palet que un AMR recoge se escanea con **RFID**: **SAP/WMS se actualiza en tiempo real** — exactitud de inventario ≥99,9%, sin escaneo manual."

## 8 · Demo en vivo (Joshua · 2:18–2:38)

**Se ve:** video del MVP (Recording MVP.mov) — NestHive operando.
**Decimos (≈20 s):** "Esto que ven es **NestHive operando el Nestlé Warehouse ahora mismo**: el mapa es la planta real, cada AMR sigue la misma lógica que seguirá en piso, y el dashboard muestra la operación en vivo — como la vería el supervisor."

## 9 · Flota: KUKA KMP 600P (Joshua · 2:38–2:58)

**Se ve:** video andén (AMR Nestlé Ecuador al andén.mp4) + specs.
**Decimos:** "La flota: **cuatro AMRs KUKA KMP 600P — tres operando, uno de backup** — importados desde Colombia, **arancel cero por la Comunidad Andina**. KUKA es el gigante alemán de la robótica — el estándar de la industria automotriz. El KMP 600P **levanta palets de 600 kilos con su elevador integrado**, navega de forma autónoma — sin cintas ni imanes: **cero obras civiles** — y habla **VDA 5050**, el idioma del WCS. Y esto no es teoría: [señalar video] un AMR así, en un andén de Ecuador."

## 10 · Cifras de impacto: no lo decimos nosotros (Andrés · 2:58–3:16)

**Se ve:** números ABB y Kostić (morph: 20→50→70, 40→85).
**Decimos:** "No lo decimos nosotros. **ABB** reporta que sistemas como este reducen hasta **20% los paros de línea**, liberan **50% del espacio de staging** y aumentan **70% la utilización del espacio disponible**. Y **Kostić y colaboradores** documentaron que la seguridad del personal sube de **40% a 85%** al eliminar la convivencia montacargas–peatón."

## 11 · Por qué cumplimos SUS criterios — 6/6 (Andrés · 3:16–3:42)

**Se ve:** tabla 6 criterios → evidencia.
**Decimos:** "Cumplimos sus criterios, uno a uno. **Innovación**: Néstor decide con percepción real — y con el algoritmo húngaro, con óptimo global. **Propuesta de valor**: techo de 411 pallets por turno — 91% más capacidad con la misma planta. **Efectividad**: 1.035 movimientos diarios, espera menor a 30 segundos y averías que no detienen la producción. **Sustentabilidad**: menos energía por pallet y una transición humana respetuosa. **Escalabilidad**: la demanda crece 5% al año y Néstor la absorbe. **Replicabilidad**: otro centro es otro archivo de configuración — el mismo Néstor."

## 12 · Gestión del cambio humano (Andrés · 3:42–4:02)

**Se ve:** gestión humana (jubilaciones, emprendimientos, 51/0).
**Decimos:** "Y lo hacemos con las personas. **Jubilaciones voluntarias** — la edad promedio del área es 45 a 60 —, **capacitación para emprendimientos**, acompañamiento familiar y psicológico, y **transferencia bidireccional de conocimiento**: el know-how operativo de la bodega entra a la era digital. Nestlé ya lo hizo con **51 personas y cero conflicto**."

## 13 · ROI — por debajo del estándar Nestlé (Andrés · 4:02–4:20)

**Se ve:** banner "≈2,4 AÑOS — POR DEBAJO DEL ESTÁNDAR NESTLÉ (2,7–3 · máx 3,5)".
**Decimos:** "¿Y la recuperación? La labor real del área es **20 colaboradores a $660 al mes — $158 mil al año**. NestHive asume el transporte interno y el equipo se reasigna a valor, más los kilómetros en vacío eliminados, la energía por pallet y las mermas: **cerca de $270 mil al año de ahorro**. Con una inversión de **$640 mil**, el **payback es de 2,4 años: por debajo del estándar Nestlé**."

## 14 · CAPEX: cómo se compone la inversión (Andrés · 4:20–4:38)

**Se ve:** tabla CAPEX + curva de payback (morph).
**Decimos:** "El desglose: cuatro KUKA KMP 600P — **$440 mil** —, importación desde Colombia — **arancel cero por la CAN, más logística: $20 mil** —, integración WCS, lectores RFID, infraestructura y puesta en marcha — $180 mil. **Total: $640 mil**. El IVA — 15% — **vuelve como crédito fiscal: no es costo**. Y si prefieren entrar por pasos: **piloto de dos AMRs, $250 mil, reversible en menos de un turno**."

## 15 · Escalabilidad y replicabilidad (Joshua · 4:38–4:52)

**Se ve:** multi-centro desde un tablero.
**Decimos:** "¿Y mañana? Otro centro de distribución es otro archivo de configuración: con demanda creciendo 5% al año, Néstor predice la saturación y planifica la siguiente inversión **antes del 85% de capacidad** — y el mismo motor opera todos los centros desde un solo tablero."

## 16 · Gracias (Joshua · 4:52–5:00)

**Se ve:** logo + "Gracias".
**Decimos:** "Somos NestHive. **La infraestructura habla con Néstor — y Néstor habla contigo.** Muchas gracias."

---

## Q&A — banco rápido (el completo vive en `nestlink/tasksR/qa_jurado_fase2.md`)

1. **Réplica anti-simulador:** "Lo que ven es el sistema operando — el mismo Néstor que, en el despliegue, se conecta al WCS de la planta. Cada cifra sale de esa operación."
2. **Números canónicos v6:** 1.035 mov/día (645 solo salida) · 215/131 por turno · takt 132 s · techo 411 (+91%) · **4 AMRs KUKA KMP 600P (3+1) desde Colombia** · CAPEX **$0,64M** (KUKA $440k + CAN 0%+$20k + integración $180k; IVA 15%=$96k recuperable) · ahorro ≈**$0,27M/año** · **payback ≈2,4 (POR DEBAJO del estándar Nestlé 2,7–3, máx 3,5)** · labor $660×20=$158,4k/año · exactitud ≥99,9% (RFID→SAP) · disponibilidad ≥98% · espera ≤30 s p95 · piloto **2 AMRs $250k** reversible <1 turno · 118+171 tests · mapa 139 nodos/162 aristas.
3. **Algoritmo húngaro (si profundizan):** matriz de costos AMR×misión; celda = w·distancia A* + prioridad P1–P10 + batería + estado + home-zone; Kuhn-Munkres O(n³) → asignación de costo mínimo global; se resuelve en ms cada vez que entra una misión o cambia la flota.
4. **¿Por qué KUKA?** Gigante alemán de robótica (estándar automotriz), KMP 600P con elevador de palets integrado, VDA 5050, soporte y distribución en LatAm (Colombia → CAN 0%).
5. **+30% costo:** "Incluso con +30% por unidad, el payback sigue ≤3,2 — dentro del estándar."
6. **Réplica AMR vs AGV:** "El AGV está esclavizado a una ruta física — cintas, imanes, obras civiles. El AMR navega autónomo: cero obras, re-ruteo dinámico real. Un tren contra un conductor."

## Checklist de ensayo

- [ ] Cronometrar los 16 bloques: contenido hasta **4:52**, "Gracias" cierra en 5:00 (tecla N = teleprompter).
- [ ] Joshua: portada (12 s), problemática con Tompkins, Néstor + **frase infraestructura**, demo con video MVP (≈20 s), flota KUKA con video andén (≈20 s), escalabilidad, cierre con la frase.
- [ ] Andrea: PLC/asignación, **algoritmo húngaro completo sin apurarse (26 s — es la slide estrella técnica)**, mantenimiento, WMS+RFID.
- [ ] Andrés: cifras ABB/Kostić de corrido, **criterios 6/6 en ≈26 s**, gestión humana, ROI (2,4 años) + CAPEX (CAN 0%, IVA recuperable, piloto $250k).
- [ ] Nadie dice "AGV", "MiR", "simulador" ni "ESPOL Fusion".
- [ ] Videos probados en el navegador: MVP con poster (click para reproducir), andén autoplay muted.
