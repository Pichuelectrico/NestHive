# NestHive — versión final de la webapp

**Estado:** versión final del escenario ESPOL Fusion, 27 de octubre de 2026.
**Repositorio:** NestHive. La planta `realistic` permanece disponible como escenario de referencia funcional.

## Qué incluye esta versión

- **Mapa ESPOL Fusion reconstruido:** grafo canónico de 139 nodos y 162 aristas, con muro perimetral y pared interior. Las rutas visibles proceden de las mismas aristas que usa la simulación. Los vehículos siguen los segmentos del grafo; se eliminaron los atajos y conexiones diagonales ajenas al diseño. El mapa mantiene 15 puntos morados de paletizaje, dos cargadores, P1–P3, R1–R3, la fuente café de Insumos y Transporte afuera a la izquierda. Los puntos azules redundantes del ramal de Insumos y B51/B73/B74 se retiraron sin cortar el corredor inferior de R3/P3.
- **Flujo de materiales:** la flota ESPOL tiene tres AGV operativos, un AGV Backup y un AGV exclusivo para Transporte. Los AGV operativos llevan insumos desde `FUENTE_INSUMOS` hasta P1, P2 o P3. La cinta se representa mediante 20 segundos de tiempo de simulación; después aparece una solicitud en R1, R2 o R3 respectivamente. El AGV exclusivo recoge los paquetes del área morada y los lleva a Transporte; se identifica en azul. Los otros AGV apoyan la exportación cuando hay sobrecarga; el Backup permanece en reserva y cubre averías. Las líneas son **R1 · Cookies**, **R2 · Chocolates** y **R3 · Wafer**.
- **Señales visuales de inventario:** 🧩 indica insumos depositados y en proceso en P. En el mismo tick en que desaparece 🧩, aparece 📦 en el R correspondiente. 📦 desaparece cuando el AGV recoge el paquete. Los puntos morados muestran 📦 mientras el paquete espera transporte.
- **Operación y mantenimiento:** todos los vehículos ESPOL se presentan como AGV. La sección «Prevención de mantenimiento de flota» muestra desgaste, estado crítico y averías. OPS permite simular una avería: el AGV se detiene, se bloquea su tramo, los demás intentan rutas alternas y se pausa la operación si no existe paso. La reparación tarda 30 segundos de simulación; mientras está detenido aparece ⚠️ sobre el AGV. Néstor y las notificaciones informan la avería y la recuperación.
- **Interfaz:** panel de KPI, flota y OPS a la izquierda; Néstor a la derecha. Se mejoró el contraste de las notificaciones. El mapa puede ampliarse y conserva la visualización de aristas, muros, nodos, flota y bloqueos en tiempo real.

La cinta transportadora y el software de diagnóstico de los AGV son **simulados** en esta versión; no existe conexión con maquinaria real. `agv-espol/` conserva la aplicación ESPOL original.

## Archivos de esta versión

| Área | Archivos | Función |
| --- | --- | --- |
| Generación del mapa | `tools/build_espol_canonical.py` | Construye el grafo y sus espejos visuales. |
| Datos de planta | `nestlink/backend/app/data/maps/espol_fusion.json`, `nestlink/backend/app/data/maps/espol_fusion_visual.json`, `nestlink/frontend/public/maps/espol_fusion.json`, `nestlink/frontend/public/maps/espol_fusion_visual.json`, `nestlink/backend/app/data/seeds/seed_espol.json` | Topología, muros, puntos, líneas y flota ESPOL. Los JSON de backend y frontend de cada mapa son idénticos byte a byte. |
| Backend y simulación | `nestlink/backend/app/api.py`, `nestlink/backend/app/chatbot.py`, `nestlink/backend/app/data_maps.py`, `nestlink/backend/app/models.py`, `nestlink/backend/app/sim/agents.py`, `nestlink/backend/app/sim/assignment.py`, `nestlink/backend/app/sim/env.py`, `nestlink/backend/app/sim/generators.py` | Misiones P→R→paletizaje→Transporte, flota y respaldo, historial acotado de misiones, estado de inventario, ruteo y mantenimiento. |
| Interfaz | `nestlink/frontend/app/globals.css`, `nestlink/frontend/components/ControlPanel.tsx`, `nestlink/frontend/components/Dashboard.tsx`, `nestlink/frontend/components/FleetBatteryPanel.tsx`, `nestlink/frontend/components/FleetChatPanel.tsx`, `nestlink/frontend/components/FleetChatWidget.tsx`, `nestlink/frontend/components/FleetDetailView.tsx`, `nestlink/frontend/components/FleetMaintenancePanel.tsx`, `nestlink/frontend/components/KanbanDetailView.tsx`, `nestlink/frontend/components/KanbanPanel.tsx`, `nestlink/frontend/components/KpiMiniPanel.tsx`, `nestlink/frontend/components/NoticeBanner.tsx`, `nestlink/frontend/components/PlantMap.tsx`, `nestlink/frontend/components/ToastStack.tsx` | Distribución, mapa, paneles, Néstor, indicadores y notificaciones. |
| Contrato frontend | `nestlink/frontend/hooks/useSimulation.ts`, `nestlink/frontend/lib/api.ts`, `nestlink/frontend/lib/mapGeometry.ts`, `nestlink/frontend/lib/mapVisualV2.ts`, `nestlink/frontend/lib/types.ts`, `nestlink/frontend/package.json`, `nestlink/frontend/package-lock.json` | Snapshots, actualización de misiones a 1 Hz, posición interpolada, renderer y dependencias. |
| Pruebas | `nestlink/backend/tests/test_amr_emergency_rule.py`, `nestlink/backend/tests/test_espol_business_flow.py`, `nestlink/backend/tests/test_espol_canonical_map.py`, `nestlink/backend/tests/test_espol_maintenance.py`, `nestlink/backend/tests/test_mission_history.py` | Flujo de pedidos, backup de flota, conectividad, rutas, averías y retención del historial. |
| Documentación | `vf.md`, `README.md`, `.gitignore` | Estado final, enlace desde el README y exclusión de skills locales. |

## Levantar y apagar la webapp

Se necesita Docker Desktop en ejecución. Desde la raíz del repositorio:

```bash
cd nestlink
docker compose -f compose.dev.yml up -d --build
```

Abrir **http://localhost:3001**. La API de desarrollo está en **http://localhost:8001**. Para ver el estado y los registros:

```bash
docker compose -f compose.dev.yml ps
docker compose -f compose.dev.yml logs -f api web
```

Para apagar ambos servicios de desarrollo:

```bash
docker compose -f compose.dev.yml down
```

El Compose estándar `nestlink/compose.yml` utiliza los puertos **3000** (web) y **8000** (API). Si se utiliza ese entorno en lugar del de desarrollo, los comandos equivalentes son `docker compose up -d --build` y `docker compose down` dentro de `nestlink/`. No iniciar los dos Compose a la vez sin comprobar que sus puertos estén libres.

## Comprobaciones de cierre

```bash
cd nestlink/frontend && npm run build
cd ../..
docker run --rm -v "$PWD/nestlink/backend:/app" -w /app nesthive-map-dev-api:latest python -m pytest tests/ -q
docker run --rm -v "$PWD/agv-espol:/app" -w /app nesthive-api:latest sh -c "pip install -q streamlit==1.64.0 >/dev/null 2>&1 && python -m pytest tests/ -q"
cmp nestlink/backend/app/data/maps/espol_fusion.json nestlink/frontend/public/maps/espol_fusion.json
cmp nestlink/backend/app/data/maps/espol_fusion_visual.json nestlink/frontend/public/maps/espol_fusion_visual.json
```

**Resultado de cierre previo:** build de Next.js correcto; 118 pruebas del backend aprobadas; 171 pruebas y 93 subpruebas ESPOL aprobadas; ambos pares de JSON idénticos. Tras el ajuste de flota e historial: build correcto y 120 pruebas backend aprobadas.

El entorno de desarrollo está aislado del despliegue en vivo. Para publicar esta versión, el responsable del despliegue debe integrar los commits y reconstruir los servicios de su entorno.
