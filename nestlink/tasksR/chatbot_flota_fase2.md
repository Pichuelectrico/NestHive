# Chatbot de flota y reporte horario — Fase 2 Loja

## 1. Concepto: consulta operacional a prueba de balas

El chatbot de NestHive es una interfaz de **intents prefijados**: cada pregunta visible en la demo corresponde a una opción fija, a una frase reconocible por keyword/regex y a una consulta determinista. No usa LLM para decidir ni para inventar respuestas. El flujo es `pregunta fija → intent conocido → endpoint NestHive → respuesta breve + datos verificables`. Si la frase no coincide, devuelve las opciones disponibles.

Esto lo hace seguro para operación, repetible en una demo en vivo y complementario al orquestador. Es un diferenciador visible frente a Mare: el operador puede preguntar y recibir contexto accionable sin abrir varias pantallas.

Preguntas prefijadas propuestas:

1. **¿Cuál es el estado de la flota?** AMRs disponibles, en misión, cargando o bloqueados.
2. **¿Cómo están las baterías?** Nivel por AMR y alertas de carga/autonomía.
3. **¿Qué misiones están en curso?** Origen, destino, AMR asignado y estado.
4. **¿Cuál es el cuello de botella ahora mismo?** Zona, pasillo o cola con mayor impacto.
5. **¿Cuál es la próxima parada de línea por stock bajo?** Línea, material, urgencia y misión asociada.
6. **¿Cómo va el turno?** KPIs actuales frente a objetivo: movimientos, takt y capacidad.
7. **¿Qué incidencias ocurrieron en la última hora?** Obstáculos, batería baja, replanificaciones y fallos.
8. **¿Cuál es la estrategia actual del orquestador?** Explica por qué asignó un AMR a una misión.
9. **¿Qué misiones se completaron en la última hora?** Conteo, tiempos y destinos.
10. **¿Qué riesgo debo vigilar ahora?** La alerta operativa prioritaria, con causa y siguiente acción.

Las respuestas deben citar hora de consulta, fuente y un pequeño conjunto de campos; nunca presentar una predicción como hecho. Si no existe dato, el bot dice “sin dato disponible” y ofrece el panel correspondiente.

## 2. Arquitectura sobre FastAPI actual

El backend ya expone los datos de la simulación y el dashboard mediante FastAPI: `GET /api/v1/fleet`, `GET /api/v1/missions`, `GET /api/v1/metrics`, `GET /api/v1/layout`, selección de planta y endpoints de simulación, además de `WS /ws` para snapshots/eventos. El chatbot debe leer esta misma fuente de verdad, no duplicar estado.

Propuesta de capas:

- `chatbot/intent_catalog.py`: catálogo versionado de intents, ejemplos de frases, keywords/regex, permisos y endpoint(s) permitidos.
- `chatbot/service.py`: normaliza la entrada, resuelve un único intent, llama al cliente interno de dominio y construye el contrato de respuesta.
- `app/api.py`: `GET /api/v1/chatbot/intents` para publicar opciones y `POST /api/v1/chatbot/query` para resolver una pregunta prefijada. Como alternativa mínima, el frontend puede llamar al servicio interno sin exponer un endpoint adicional.
- `chatbot/hourly_report.py`: agrega eventos/KPIs por ventana horaria y publica el reporte al dashboard y al WebSocket.

Mapeo inicial (un intent puede combinar lecturas, pero nunca escribir):

| Intent | Fuente existente |
|---|---|
| estado de flota / baterías | `GET /api/v1/fleet` |
| misiones en curso / completadas | `GET /api/v1/missions` + métricas de la ventana |
| KPIs del turno / riesgo | `GET /api/v1/metrics` |
| cuello de botella / próxima parada | `GET /api/v1/missions`, `GET /api/v1/metrics`, y layout si hace falta contexto espacial |
| incidencias | registro de eventos del simulador; si no existe una vista consolidada, añadir un endpoint de lectura de incidencias |
| estrategia del orquestador | telemetría explicativa de asignación; si no está expuesta, añadir `GET /api/v1/decisions/latest` de solo lectura |

Contrato de respuesta sugerido:

```json
{
  "intent": "fleet_status",
  "text": "4 AMRs en misión, 1 disponible y 1 cargando.",
  "data": {"in_mission": 4, "available": 1, "charging": 1},
  "as_of": "2026-10-27T10:00:00-05:00",
  "source": "/api/v1/fleet"
}
```

La UI muestra botones de preguntas, texto corto y tarjetas de datos; no habilita texto libre como ruta de decisión. El servicio debe tener timeout, respuesta “dato no disponible” y logs del intent para auditar la demo.

## 3. Reporte automático cada hora

Un scheduler del backend ejecuta cada 60 minutos (y permite un `POST` manual en modo demo) un agregador de la ventana anterior. El reporte contiene: misiones completadas, vacíos evitados, paradas evitadas, km evitados, incidencias, movimientos, takt y demás KPIs disponibles. Se persiste como registro inmutable con `window_start`, `window_end`, `created_at`, métricas y versión de cálculo.

El dashboard muestra una tarjeta “Último reporte horario”, histórico de reportes y estado de la próxima ejecución. El backend emite por `WS /ws` un evento `hourly_report_ready` para refrescar la tarjeta sin recargar. En la demo: se ejecuta una ventana acelerada o el botón “Generar reporte”, el sistema sigue la operación en vivo, aparece el evento y el operador pregunta “¿qué pasó en la última hora?” para obtener exactamente el mismo resumen.

Si el proceso reinicia, el scheduler debe ser idempotente por ventana horaria: no duplica reportes y reconstruye el agregado desde eventos/KPIs persistidos. La periodicidad real no cambia los números canónicos del caso.

## 4. Encaje SAP EWM/WMS/WCS

El chatbot **lee, no escribe**. NestHive sigue siendo la capa de orquestación de AMRs: consulta el estado operativo y presenta una vista unificada, mientras SAP EWM/WMS conserva órdenes e inventario y WCS/controles conserva la ejecución de equipos. La integración inicial puede consumir APIs, eventos o réplicas de lectura sin enviar comandos a sistemas productivos.

Este límite reduce el riesgo de integración a prácticamente cero para el piloto y fortalece la Factibilidad (20 %): no se reemplaza SAP/WMS/WCS ni se exige modificar su lógica. En una fase futura, comandos como “pausar misión” requerirían autenticación, roles, doble confirmación, trazabilidad, idempotencia y una API explícita de escritura; no forman parte de esta demo.

## 5. ROI y valor operativo

El coste marginal es aproximadamente **$0** en CAPEX adicional: es software sobre el backend y dashboard existentes, con un esfuerzo de días-dev para catálogo, agregación y UI. No añade AMRs ni modifica infraestructura.

El valor es visibilidad inmediata para el operador, sustitución del reporte manual por radio/Excel, trazabilidad horaria y una explicación comprensible de las decisiones del orquestador. Se apoya en el caso base de **1.035 mov/día**, techo de **411 pallets/turno**, CAPEX de **$0,95M**, ahorro de **$0,21M/año** y payback de **4,5 años** (≤3 con 3 turnos). El piloto reversible de **2 AMR por $0,22M**, en menos de 1 turno, permite validar adopción del chatbot sin comprometer operación.

## 6. Mensaje para la slide y preguntas del jurado

### Cinco bullets para slide

- Preguntas prefijadas: cero LLM, cero alucinación, respuesta repetible.
- Una vista para flota, misiones, batería, incidencias y estrategia.
- Reporte automático cada 60 min, visible en dashboard y por WebSocket.
- Lee SAP EWM/WMS/WCS; no escribe: riesgo de integración prácticamente cero.
- Diferenciador de demo: visibilidad accionable sobre 1.035 mov/día con coste marginal ≈ $0.

### Tres preguntas del jurado

**¿Por qué no usar un LLM?** Porque en operación priorizamos seguridad y auditabilidad: el catálogo prefijado limita la superficie de error y cada respuesta apunta a datos reales de NestHive.

**¿Van a reemplazar SAP o el WMS/WCS?** No. El chatbot solo lee y unifica la operación de AMRs; SAP EWM/WMS y WCS siguen siendo los sistemas de registro y ejecución. La escritura queda para una fase con roles y controles.

**¿Qué retorno aporta si el ahorro principal ya está en la automatización?** Convierte telemetría en decisiones y trazabilidad: menos tiempo buscando información, menos reportes manuales y mejor reacción ante incidencias. Se entrega sobre la plataforma existente, sin cambiar el CAPEX, el ahorro de $0,21M/año ni el payback de 4,5 años.

## 7. Endpoints implementados (NestHive)

- `GET /api/v1/chat/asks`: catálogo de las 10 preguntas prefijadas.
- `GET /api/v1/chat/ask?q=...`: resolución determinista por keywords sobre el estado real del simulador; devuelve `{answer, data, ts}`.
- `GET /api/v1/chat/report`: último reporte horario simulado, con movimientos, pallets entregados, incidencias, flota y KPIs.
- `WS /ws`: además de snapshots, difunde el evento `hourly_report_ready` al cerrar cada hora simulada.
