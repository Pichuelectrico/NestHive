# NestLink Frontend

Dashboard Next.js 14 del MVP NestLink (Hackathon InnoLabs Nestlé).

## Arranque rápido

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:3000

## Variables de entorno (opcional)

Crea `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

Si el backend no responde en 3s, el front entra en **modo demo offline** (seed 42) automáticamente.

## Estructura

- `app/` — App Router (layout, page)
- `components/` — Dashboard, mapa Canvas, kanban, gauges, KPIs, controles
- `hooks/` — WebSocket + offline demo, layout fetch, LERP 60fps
- `lib/` — tipos API, cliente REST, motor demo offline
- `public/maps/plant_layout.json` — fallback del mapa 2D

## Contrato

Ver `../docs/API_CONTRATO.md` para snapshots WebSocket y endpoints REST.
