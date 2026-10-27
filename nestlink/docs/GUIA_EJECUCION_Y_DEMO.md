# Guía Operativa de Ejecución y Guion de Demo — NestLink (Reto 1)
**Manual de Despliegue, Run Book, Plan B y Pitch de 5 Minutos | Hackathon InnoLabs Nestlé**

---

## 1. Cómo Levantar el Stack Completo (Run Book)

El stack de NestLink está desacoplado en dos capas: Backend FastAPI (motor de simulación, ruteo A*, asignador húngaro y WebSockets) y Frontend Next.js (Canvas 2D interactivo, Kanban de misiones y panel de KPIs).

```
┌────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js 14 / React)                         │
│  http://localhost:3000                                 │
└───────────────────────────▲────────────────────────────┘
                            │ WS: ws://localhost:8000/ws
                            │ REST: http://localhost:8000/api/v1
┌───────────────────────────▼────────────────────────────┐
│  BACKEND (Python / FastAPI / NetworkX / Scipy)         │
│  http://localhost:8000 (Docs: /docs)                   │
└────────────────────────────────────────────────────────┘
```

### 1.1 Paso 1: Levantar el Backend (FastAPI)
Abrir una terminal en la MacBook del Backend y ejecutar:

```bash
cd /Users/joshuareinoso/Downloads/Hackathon_InnoLabs_MVP_Plan/backend

# 1. Crear y activar entorno virtual (si no existe)
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor FastAPI con Uvicorn en el puerto 8000
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

### 1.2 Paso 2: Levantar el Frontend (Next.js)
Abrir una segunda terminal en la MacBook del Frontend y ejecutar:

```bash
cd /Users/joshuareinoso/Downloads/Hackathon_InnoLabs_MVP_Plan/frontend

# 1. Instalar dependencias
npm install

# 2. Iniciar servidor de desarrollo en el puerto 3000
npm run dev
```

### 1.3 Configuración de Variables de Entorno
Verificar `.env.example` en la raíz (copiar a `.env.local`, no commitear):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### 1.3b Alternativa Docker (cuando `compose.yml` esté disponible)

```bash
docker compose up --build
# front http://localhost:3000, back http://localhost:8000, healthcheck en /health
```
`NEXT_PUBLIC_*` se pasa como build ARG del frontend.

### 1.4 Verificación de Arranque y Salud del Stack
Ejecutar en una terminal para validar que el backend y la simulación están activos:

```bash
# 1. Comprobar Healthcheck del Backend
curl -s http://localhost:8000/health | jq .
# Salida esperada: {"status": "ok", "version": "1.0.0", "sim_running": true}

# 2. Comprobar Carga del Layout Canónico
curl -s http://localhost:8000/api/v1/layout | jq '.canvas.title'
# Salida esperada: "Planta Nestlé — Gemelo Intralogístico NestLink"

# 3. Comprobar Flota Inicial
curl -s http://localhost:8000/api/v1/fleet | jq 'length'
# Salida esperada: 5
```

4. Abrir en el navegador: **`http://localhost:3000`**.  
   *Señal de éxito:* El mapa de la planta debe mostrar los 5 AMRs en movimiento fluido, los peatones patrullando y el feed WebSocket en estado verde (`Conectado`).

---

## 2. Guion de Demo End-to-End Cronometrado (Pitch de 5 Minutos)

> **Tagline Oficial:**  
> *"NestLink: No proponemos comprar más robots, proponemos el cerebro que hace que 5 AMRs rindan como 10."*

| Minuto | Mensaje / Qué Decir | Acción en Pantalla (Qué Clicar / Mostrar) | Qué se Ve en la UI |
| :--- | :--- | :--- | :--- |
| **0:00 – 0:30** | *"Buenos días jurado. Una línea parada en Nestlé cuesta miles de dólares por hora. Hoy en día, el movimiento de materiales depende de montacargas manuales que viajan vacíos el 30% del tiempo y pedidos por radio cuando la línea ya se quedó sin bobinas. NestLink es el cerebro orquestador que automatiza este flujo."* | Proyectar diapositiva inicial con foto de planta y métrica de dolor (30% viajes vacíos). | Diapositiva 1 / Portada. |
| **0:30 – 1:15** | *"Aquí ven a NestLink en vivo: el gemelo digital de nuestra planta. Tenemos 5 AMRs Nestlé transportando café Nescafé, chocolates Savoy y caldos Maggi entre líneas y almacén en tiempo real."* | Cambiar al navegador (`http://localhost:3000`) a pantalla completa (`F11` o `Cmd+Shift+F`). | Mapa oscuro de la planta con nodos interconectados, AMRs con aros de color según estado (`MOVING`, `LOADING`, `IDLE`) y peatones patrullando. |
| **1:15 – 2:00** | *"Cada necesidad genera una misión que entra a nuestra cola priorizada. El algoritmo Húngaro asigna el AMR óptimo en milisegundos y A* calcula la ruta más corta sin viajes vacíos."* | Señalar el panel **Kanban de Misiones** a la derecha y el selector de AMRs. | El Kanban se reordena en vivo; las tarjetas pasan de `Pendiente` a `En Curso` y `Completada` automáticamente. |
| **2:00 – 3:00** | **MOMENTO WOW 1 (Incidente):** *"¿Qué pasa en un imprevisto? Simulamos un derrame de líquido en el pasillo central."* <br><br> **MOMENTO WOW 2 (Seguridad):** *"Además, observen al operario Carlos cruzando el pasillo: el AMR-02 detecta su presencia a 2.5 metros y se detiene por seguridad."* | 1. Clic en botón **«Simular Derrame X_02 ↔ X_05»** en el panel de incidentes.<br>2. Clic en botón **«Inyectar Pico de Demanda en E1 Savoy»**. | 1. La arista central se pinta **roja brillante**; los AMRs que iban por ahí giran y toman el pasillo este de inmediato.<br>2. El AMR frena en seco, su aro cambia a naranja (`WAITING_OBSTACLE`), y reanuda cuando el peatón pasa. |
| **3:00 – 3:45** | **MOMENTO WOW 3 (Pico & Flota Viva):** *"Vean qué ocurre ante un pico imprevisto en una línea: NestLink inyecta la misión crítica `SUPPLY_REQUEST` (P10) y los AMRs rebalancean su flota en tiempo real."* <br><br> **MOMENTO WOW 4 (Rellenado Estratégico $\ge 80\%$):** *"Con el botón 'Rellenar 80%', NestLink encadena entregas continuas hasta que la línea seleccionada supera su stock de seguridad."* | 1. Elegir en el dropdown una línea de marca (**Nescafé, MAGGI, Savoy, La Lechera**) y clic en **«Inyectar Pico de Demanda»**.<br>2. Observar al AMR (y al Nestlé Runner) asistir abasteciendo desde el almacén MP **de esa marca**.<br>3. Clic en botón **«Rellenar 80% / TODAS»**. | 1. La barra de la línea baja y emite un banner de alerta; se encola de inmediato la misión P10.<br>2. El AMR sale del Almacén MP de la marca correspondiente (p.ej. Nescafé→WH_MP_3).<br>3. Al completar la entrega, el nivel sube **+20% por viaje** (~4 viajes por línea) y se re-encadena hasta $\ge 80\%$. |
| **3:45 – 4:00** | **Ronda 5.2 (Cola reactiva):** *"Y si el supervisor quiere probar la orquestación: reiniciamos la cola y sumamos misiones al vuelo."* | 1. Botón **⟳ Reiniciar tareas** (`POST /api/v1/sim/reset_missions`).<br>2. Botones **＋5 / −5 misiones** (`POST /api/v1/sim/adjust_missions {delta: ±5}`) para inflar/vaciar la cola y ver al asignador húngaro reaccionar. | La cola (kanban) se limpia y luego crece/decrece en vivo; AMRs se reasignan. |
| **3:45 – 4:15** | **MOMENTO WOW 5 (Gestión Energética & Autocarga):** *"Los AMRs consumen batería en tiempo real mientras se desplazan. Si caen a $\le 15\%$, NestLink los reparte entre las dos estaciones de carga: cada AMR elige el cargador libre más cercano considerando ocupación y distancia, evitando colas en un solo cargador, y se recarga al 100% antes de retomar."* | Clic en el botón **«🔋 15% Batería»** en cualquier AMR de la lista (probar con 2 AMRs seguidos para ver el reparto). | El AMR cambia a 15%, recibe `RECHARGE` (P8) y se dirige al cargador libre más cercano; si `CHARGER_1` está ocupado, el siguiente va a `CHARGER_2`. Entra en `CHARGING`, sube a 100% y vuelve a `IDLE`. |
| **4:00 – 4:45** | *"Escalabilidad pura: NestLink no requiere obra civil ni hardware propietario. Cambiar de planta en Cayambe o Guayaquil es tan simple como cargar un nuevo archivo JSON de layout."* | Mostrar el modal de cambio de layout o la arquitectura API abierta. | Gráfica de payback estimado (14–18 meses) y métricas de sostenibilidad (reducción de kWh y huella de carbono). |
| **4:45 – 5:00** | *"NestLink es el Waze y el cerebro intralogístico para Nestlé. Muchas gracias."* | Cierre en diapositiva final con integrantes del equipo y GitHub QR. | Pantalla de cierre. |

---

## 3. Plan B Offline (Garantía Cero "Demo Effect")

Si durante la presentación falla la red Wi-Fi del auditorio o el servidor backend local se detiene:

### 3.1 Activación del Modo Offline en el Frontend
El frontend incluye un simulador client-side autónomo respaldado por `seed=42`:
1. En la esquina superior derecha del dashboard, hacer clic en el toggle **«Modo: Backend / Demo Offline»** (o usar el atajo de teclado **`Ctrl + Shift + D`**).
2. El frontend cargará inmediatamente el layout desde `/maps/plant_layout.json` y comenzará a generar los mismos ticks de simulación deterministas internamente con `setInterval`.
3. Todos los botones de la demo (**Derrame en X_02**, **Pico de Demanda**, **Peatón**) funcionan de forma idéntica en modo offline.

---

## 4. Checklist Pre-Evento (Día 4 de Septiembre — 8:00 AM)

Realizar este checklist en las dos MacBooks antes de iniciar las presentaciones:

- [ ] **Validación de Funcionalidades R5:**
  - Probar botón **«Inyectar Pico»** y verificar banner + misión `SUPPLY_REQUEST` generada.
  - Probar botón **«Rellenar 80% / TODAS»** (`POST /api/v1/sim/refill`) y confirmar llenado continuo.
  - Probar botón **«🔋 15% Batería»** (`POST /api/v1/sim/low_battery`) y confirmar ruta hacia cargador y estado `CHARGING`.
  - Probar selector de planta (`Quito` y `CD Guayaquil`) validando carga de mapa en caliente.
- [ ] **Puertos Libres:** Verificar que los puertos `8000` y `3000` no estén ocupados por otros procesos:
  ```bash
  lsof -ti:8000,3000 | xargs kill -9 2>/dev/null || true
  ```
- [ ] **Versiones de Entorno:**
  - Python $\ge$ 3.10 (`python3 --version`)
  - Node.js $\ge$ 18.x (`node --version`)
- [ ] **Dependencias Preinstaladas:** Correr `pip install -r requirements.txt` y `npm install` con anticipación para no depender de descargas de internet durante el hackathon.
- [ ] **Resolución y Pantalla:** Configurar la pantalla a formato **16:9** (1920×1080 o 1440×900) con zoom del navegador al 100% para que el canvas de 800×500 y los paneles laterales calcen sin scroll vertical.
- [ ] **Reposo y Notificaciones:** Desactivar suspensión de pantalla y activar modo *No Molestar* en la MacBook de presentación.

---

## 5. Notas de Integración Frontend ↔ Backend

Lista de verificación técnica para validar cuando ambos componentes estén corriendo:

| Componente / Endpoint | Verificación Esperada | Estado |
| :--- | :--- | :---: |
| `GET /health` | Retorna `status: ok` y `sim_running: true`. | `[x]` |
| `GET /api/v1/layout` | Retorna grafo conexo con 22 nodos y 30 aristas. | `[x]` |
| `GET /api/v1/fleet` | Retorna los 5 AMRs con sus posiciones y baterías. | `[x]` |
| `GET /api/v1/missions` | Retorna la lista activa de tareas en cola. | `[x]` |
| `POST /api/v1/obstacles/block` | Marca arista como bloqueada y recalcula rutas $A^*$. | `[x]` |
| `POST /api/v1/sim/peak` | Reduce nivel de material en empacadora seleccionada. | `[x]` |
| `WS /ws` | Emite payload `SimulationSnapshot` estable a 5 Hz. | `[x]` |
