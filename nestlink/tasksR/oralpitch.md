# Oral Pitch — Guion slide a slide (12 slides + Q&A oratoria)

Guion hablado para la demo del **Hackathon InnoLabs Nestlé** · 4-sep-2026.
Cada bloque es lo que se espera **decir** en su slide del deck `tasksR/pitch_deck/index.html`.
Separamos las slides con `---`. Ritmo: frases cortas, fluido, sin tecnicismos innecesarios.

---

## Slide 1 · Portada

**Qué se ve:** Título NestLink + claim + logo.

**Qué decimos:**
"Buenas tardes. Somos NestLink y hoy les vamos a mostrar cómo automatizamos y optimizamos el flujo de materiales y producto entre producción y almacén, con robots móviles y visión por computadora. Es una solución real: lo que van a ver corre en vivo."

---

## Slide 2 · Eje 1 · Problemática

**Qué se ve:** La pregunta central del reto + el doble flujo (producción → almacenamiento y almacén → empaque) + costos ocultos.

**Qué decimos:**
"Nestlé nos pidió algo muy concreto: cómo automatizar y optimizar el movimiento de material y producto entre producción y almacenamiento. Hay dos flujos: el producto terminado que sale de las líneas y hay que llevarlo al almacén, y los materiales que deben llegar a tiempo a las máquinas empaquetadoras. Hoy, ese movimiento depende en gran parte de personas: intervención manual, recorridos repetitivos y puntos de entrega que, si se descuidan, pueden complicar la operación. Ese es el dolor que atacamos."

---

## Slide 3 · Eje 2 · Solución y Viabilidad

**Qué se ve:** Arquitectura end-to-end + flota dimensionada + hardware (MiR1200) + transferencia + precisión de toma.

**Qué decimos:**
"Nuestra solución es una flota de AMRs coordinada por capas: percepción con sensores y visión, detección de peatones en tiempo real y un controlador de misión que dice a cada robot qué, por dónde y cuándo. Y está dimensionada a su realidad: para mover los 215 pallets mínimos al día necesitamos seis MiR1200 — cinco de línea continua y uno de reserva, que además toma las acciones prioritarias y lleva el tramo exclusivo del montacargas por su corredor rosado. ¿Por qué horquillas y no una tapa plana? Porque la tapa plana, la opción más barata, solo sirve si hay operarios en ambos extremos: el pallet se carga y descarga a mano. Nosotros acoplamos el robot a una cinta de rodillos a la misma altura: la caja sale del encartonador, cae al robot y él la entrega a la mesa en bodega; nadie toca la carga. Y como meter las horquillas exige milímetros y la navegación natural da centímetros, usamos navegación natural en el trayecto y referencia local en la toma: cámara que lee la ventana del pallet, marcador fiducial o detección de patas. Viable en entorno industrial, modular, sobre su propia planta."

---

## Slide 4 · Demo en vivo

**Qué se ve:** Diagrama completo del ciclo: líneas → paletizado → 4 OUTs → AMR 6 por la ruta rosada → muro externo + dashboard con KPIs en vivo.

**Qué decimos:**
"Vamos a la demo. Miren el ciclo completo: la materia prima llega a las líneas de forma preventiva, antes de que se vacíen; un AMR recoge cada paquete de producción, lo lleva a paletizado y lo deja listo en uno de los cuatro puntos de salida. De ahí, el AMR 6 — rosado, el único con ruta exclusiva, que asume el rol del montacargas — lo lleva hasta el muro externo de entrega, separado del área de producción. Noten la robustez: si el AMR 6 necesita recargar, completa primero la entrega y recién va a cargar. Y miren el tablero: viajes completados, paradas evitadas, tiempo en puntos de salida y el ROI de la flota, todo subiendo en vivo."

---

## Slide 5 · Eje 3 · Innovación

**Qué se ve:** 4 cards: misión por nodo, robustez, realidad simulada + Ciberseguridad / AMRs propios.

**Qué decimos:**
"¿Qué nos diferencia? Tres cosas. Primero, control por misión en cada punto, no un WMS que reparte tareas a ciegas: cada entrega se coordina de forma inteligente y elimina los puntos de entrega sin control de estado, que tienden a complicar la operación. Segundo, robustez real: si un robot de entrega debe cargar, completa la entrega antes de ir a cargar; tolerancia a fallos en operación, no en teoría. Y tercero, lo construimos sobre una réplica digital de la planta: todo lo que ven corrió antes en simulación, con ciberseguridad y AMRs propios, no cajas negras importadas."

---

## Slide 6 · Eje 4 · Propuesta de valor

**Qué se ve:** 4 cards de impacto: productividad, seguridad, OUTs siempre disponibles, repo de planta configurable.

**Qué decimos:**
"Para las operaciones de Nestlé el valor es directo: más productividad porque los robots no se detienen y los puntos de salida están siempre disponibles; más seguridad, porque la flota detecta a las personas y evita colisiones — cero incidentes; y una réplica digital de la planta que se configura, no se reprograma: escalar a otra línea o a otro centro es cuestión de datos, no de desarrollo. Esto no vende una máquina: vende productividad, seguridad y eficiencia medidas — más metros por hora de flota, menos riesgo operativo y menos energía por pallet."

---

## Slide 7 · Inversión y retorno

**Qué se ve:** Inversión ≈ US$ 0,95 M (6× MiR1200 + Fleet + cargadores + transferencia + integración) · beneficios ≈ US$ 0,20 M/año · "Así se cubre la inversión" · payback ≈ 4,5 años.

**Qué decimos:**
"Y el costo, con honestidad. Implementar la flota hoy cuesta alrededor de 950 mil dólares: seis MiR1200, el software de flota, los cargadores, los acoples de transferencia y su integración a la línea. Pero la flota se paga sola. Al año ahorramos cerca de 200 mil dólares: horas de operario liberadas de las tareas de montacargas, kilómetros y energía que evitamos recorrer, menos mermas por paradas innecesarias y cero incidentes. Si dividimos la inversión entre el ahorro anual, la recuperamos en torno a cuatro años y medio — y en un escenario de tres turnos con mano de obra cara, en la mitad del tiempo. Hay que invertir, pero cada pallet movido devuelve parte de esa inversión, hasta que la flota se paga y empieza a producir."

---

## Slide 8 · Eje 5 · Sostenibilidad

**Qué se ve:** Net Zero / uso eficiente de recursos + aportes medibles (paradas, energía, papel).

**Qué decimos:**
"La eficiencia también es sostenibilidad. Al evitar viajes en vacío, consumo de energía, piezas desgastadas; al eliminar paradas innecesarias, reducción de mermas. Son menos kilómetros recorridos, menos desperdicio y una operación más limpia, alineada con el compromiso Net Zero de Nestlé. En una frase: hacemos más pallets con menos electricidad, menos horas y menos desperdicio — eficiencia de recursos con números, no con eslóganes."

---

## Slide 9 · Eje 6 · Escalabilidad

**Qué se ve:** Demostrable hoy (4-6 robots) → operación completa (10-15) → multi-centro; mapa de centro + KPI por réplica.

**Qué decimos:**
"Esto no queda en una planta. La misma arquitectura — percepción, controlador de misión, réplica digital — se replica en cualquier centro Nestlé: se ajustan los mapas, la cantidad de robots y el ritmo, y la operación se levanta igual. De demostrables hoy a una operación completa de diez o quince robots, y luego a varios centros con los mismos KPIs midiendo el mismo resultado. Porque lo que hoy corre para una planta es el mismo motor que mañana coordina un grupo de centros desde un solo tablero."

---

## Slide 10 · Cierre

**Qué se ve:** Demo en pantalla + mensaje final (problema, solución, diferencial).

**Qué decimos:**
"En resumen: atacamos el problema real que planteó Nestlé — el flujo entre producción y almacén — con una solución viable, innovadora y escalable. Los dejamos con la demo en pantalla y estamos listos para sus preguntas. Y si quieren verlo funcionar, la demo en vivo queda publicada en la web."

---

## Q&A · solo oratoria (no hay slide en el deck)

Las preguntas se responden sin support visual: se deja la lámina de Cierre (o la demo en vivo) en pantalla. Respuestas para apoyarse:
- *"¿Y si un robot de entrega debe cargar?"* → "La entrega se completa antes de la recarga, cero pérdidas."
- *"¿Cómo perciben a las personas?"* → "Visión computacional + sensores: detectan al peatón y re-rutean al instante."
- *"¿Qué pasa con su WMS?"* → "Nos integramos; no lo reemplazamos."
- *"¿Cuánto cuesta?"* → "Seis MiR1200 dimensionados a sus 215 pallets/día. La transferencia más barata es la tapa plana manual, pero elegimos el acople a cinta de rodillos para la autonomía del fin de línea. Se paga con lo que se evita en viajes vacíos, paradas y mermas; de ahí el ROI."
- *"¿Puede ir a otra planta?"* → "Se configura el nuevo mapa: los datos, no el desarrollo, son los que cambian."

---

## Slide 11 · Apéndice A · Origen de los KPIs

**Qué se ve:** Tabla KPI → fórmula → fuente (viajes, tiempos de entrega, paradas evitadas, km evitados, tiempo en OUT, ROI).

**Qué decimos:**
"Detalle corto de dónde salen los números. Los viajes completados y el tiempo medio de entrega se registran en el cierre de cada viaje de entrega. Las paradas evitadas se cuentan cada vez que el control preventivo actúa antes de que una línea se vacíe. Los kilómetros evitados se estiman por viaje, y el ROI es la fracción de kilómetros evitados sobre el total recorrido. El tiempo en puntos de salida se mide desde que el paquete llega al OUT hasta que se despacha. Todo se mide dentro de la simulación y es verificable en los tests."

---

## Slide 12 · Apéndice B · Comparativa con modelo humano

**Qué se ve:** Tabla humano/montacargas vs NestLink (exactitud, robustez, personas, escalabilidad) + ahorro por viaje.

**Qué decimos:**
(Transición: cerrada la demo y los datos, pasamos a la comparación con la operación humana.)
"Y la comparación honesta. Un operador con montacargas es una persona que se cansa, puede olvidarse y tarda más; si un punto de entrega se descuida, tiende a complicar la operación. NestLink camina igual que la operación humana — los robots siguen la misma planta — pero sin cansancio, sin olvidos, con tolerancia a fallos, y cada viaje consolidado ahorra cerca de 0.14 kilómetros. Menos distancia, menos personas en tareas repetitivas, misma fábrica."

---

*Notas: deck `index.html` = 12 slides (la Q&A vive solo en este guion, sin slide), sin timings ni notas de orador en las slides. Este guion es el complemento hablado.*
