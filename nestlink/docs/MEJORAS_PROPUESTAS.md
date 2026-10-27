# Mejoras Propuestas — NestLink

> Etiquetas: **(a) pre-evento** = hacer antes del 4 sept · **(b) post-evento** = roadmap para pitch/escalabilidad · **(c) opcional-nice**

## 1) Docker Compose completo (front + back + red interna) — (a) pre-evento ✔️ en implementación (Antigravity: compose.yml)

- **Qué:** `Dockerfile` para `backend` (python:3.11-slim, `pip install -r requirements.txt`, `uvicorn app.main:app --host 0.0.0.0 --port 8000`) + `Dockerfile` para `frontend` (node:20-alpine, `npm ci && npm run build`, `next start`), `compose.yml` con servicios `api` y `web`, red `nestlink`, `healthcheck` en `api` (`curl /health`), `depends_on: condition: service_healthy` en `web`, variables `NEXT_PUBLIC_API_URL` y `SIM_SPEED_FACTOR`.
- **Aporta:** `docker compose up --build` levanta todo en cualquier Mac sin instalar deps; elimina "en mi máquina sí funciona" el día del evento y sirve como argumento de profesionalismo ante el jurado.
- **Esfuerzo:** **M** (2–3 h) · **Impacto:** Alto · **Riesgo si no se hace:** fricción de setup en USFQ.

## 2) Variables de entorno y secrets — (a) pre-evento ✔️ implementada (raíz/.env.example + frontend lib/config.ts)

- **Qué:** Centralizar `NEXT_PUBLIC_API_URL`, `SIM_SPEED_FACTOR`, `CORS_ORIGINS` en `.env.example` + `.env.local` (no commitear secrets). Validar en `config.ts` y `settings` de FastAPI con `pydantic-settings`.
- **Aporta:** Cambiar de `localhost` a IP del venue o a URL de deploy sin tocar código.
- **Esfuerzo:** **S** (30 min) · **Impacto:** Medio.

## 3) Type checking estricto + lint + formateo (pre-commit) — (a) pre-evento ✔️ en implementación

- **Qué:** `tsc --noEmit`, ESLint, Prettier, `ruff`/`black` en backend, `pre-commit` hooks + `lint-staged`.
- **Aporta:** Evita bugs tontos bajo presión del hackathon.
- **Esfuerzo:** **S** · **Impacto:** Medio.

## 4) Tests de integración + test de WebSocket — (a) pre-evento

- **Qué:** Ampliar `tests/` con: test de `block/unblock` y reruteo A*, test de `peak`, test de WS que recibe 3 snapshots y valida schema `Snapshot`. Usar `httpx` + `pytest-asyncio`.
- **Aporta:** Confianza para refactors de última hora.
- **Esfuerzo:** **M** (2 h) · **Impacto:** Medio-Alto.

## 5) CI/CD con GitHub Actions — (b) post-evento (c si sobra tiempo)

- **Qué:** Workflow `ci.yml`: `pip install + pytest`, `npm ci + tsc + build`, opcional `docker build`.
- **Aporta:** Señal de madurez para el pitch de escalabilidad; no crítico el día del evento.
- **Esfuerzo:** **S** · **Impacto:** Medio.

## 6) Telemetría / logging / observabilidad — (b) post-evento

- **Qué:** `structlog` o `loguru` en back, logs JSON por tick (opcional), endpoint `/metrics` prometheus, front con `console` agrupado.
- **Aporta:** Debug y storytelling con datos reales ("ver el log de reruteos").
- **Esfuerzo:** **S–M** · **Impacto:** Bajo para el jurado, alto para operación real.

## 6b) Refill dirigido al 80% + ciclo de batería completo — (a) pre-evento ✔️ implementada (Ronda 5)

- **Qué:** Meta de insumos encadenada (cada entrega suma 65% y se re-encola SUPPLY hasta alcanzar el objetivo ≥80% por línea) vía `POST /api/v1/sim/refill` + botón front. Se añadió **consumo de batería en tránsito** y **autocarga orgánica** (≤15% → RECHARGE al cargador) para que la flota trabaje de forma continua y se aprecie el desvío a carga y el apoyo del AMR comodín.
- **Aporta:** Resuelve "todos terminaron rápido y nadie tiene insumos altos"; da vida al demo (flota activa, baterías bajando, vuelos a cargador, Nestlé Runner como refuerzo).
- **Esfuerzo:** Hecho (backend + api contract + tests 27/27; frontend en curso).

## 7) Seeds y escenarios demo más realistas + multi-planta — (b) post-evento ✔️ en implementación (segundo layout para escalabilidad)

- **Qué:** `seed.json` por escenario (turno normal, pico, mantenimiento), selector en UI; segundo `plant_layout.json` (CD Guayaquil) para demostrar "cambiar de planta = cambiar JSON".
- **Aporta:** Argumento estrella de **escalabilidad y replicabilidad** (15% del puntaje).
- **Esfuerzo:** **M** · **Impacto:** Alto en pitch.

## 8) Persistencia (SQLite/Postgres) para histórico real — (b) post-evento

- **Qué:** Guardar misiones y KPIs por tick en DB (SQLModel/SQLAlchemy), endpoint `/api/v1/history`.
- **Aporta:** Gráficos de tendencias con datos reales en vez de mock; habilita analítica post-evento.
- **Esfuerzo:** **L** · **Impacto:** Medio (no necesario para ganar el hackathon).

## 9) Deploy + HTTPS/WSS (Caddy/nginx) — (b) post-evento

- **Qué:** Reverse proxy con TLS automático (Caddy), `wss://` para WS en producción, deploy en VPS (Fly/Render) vs Vercel+Render.
- **Aporta:** Demo pública sin `ws://` bloqueado por el navegador.
- **Esfuerzo:** **M** · **Impacto:** Alto si quieren mostrar fuera de USFQ.

## 10) Autorización simple (roles operador/admin) — (c) opcional-nice

- **Qué:** Middleware simple con API key o JWT, roles `operador` (solo ver) vs `admin` (block/peak).
- **Aporta:** Realismo industrial; no aporta puntos directos del jurado.
- **Esfuerzo:** **M** · **Impacto:** Bajo.

---

### Priorización

| Prioridad | Mejora |
|-----------|--------|
| Hacer ya (a) | 1 Docker Compose, 2 env/secrets, 4 tests WS, 3 lint |
| Después (b) | 7 multi-planta, 9 deploy HTTPS, 5 CI, 6 observabilidad, 8 persistencia |
| Si sobra tiempo (c) | 10 auth, heatmap tráfico, comparativa "sin NestLink" |

### Mejoras de UI de recorrido/animación

Ver **docs/MEJORAS_UI_ROUTING.md** — emojis de carga/batería, estela de ruta por tipo de misión y animaciones del recorrido (solo frontend, sin backend).

### Docker Compose — esqueleto sugerido

```yaml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    healthcheck: { test: ["CMD","curl","-f","http://localhost:8000/health"], interval: 10s, retries: 5 }
  web:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      api: { condition: service_healthy }
```
