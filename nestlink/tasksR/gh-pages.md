# GitHub Pages — despliegue del MVP (rama JoshR)

## 1. Activar Pages (LO HACE EL DUEÑO DEL REPO — requiere admin)
Settings → Pages → **Source: "GitHub Actions"** → Save.
- Es imprescindible para `actions/deploy-pages`. Con el repo público y plan free ya es posible.
- El token del team solo tiene push (no admin): `gh api …/pages` devuelve 404 mientras Pages no exista. El comando lo debe correr el dueño:
  - `gh api -X POST repos/Mare1225/NestLink/pages -f build_type=workflow`
- URL resultante: https://Mare1225.github.io/NestLink/

## 2. CI (ya activo)
`.github/workflows/deploy-gh-pages.yml`:
- Triggers: push a `JoshR` (paths `frontend/**`) + `workflow_dispatch`.
- Build: ubuntu, node20, `npm ci`, y
  `NESTLINK_PAGES=1 NESTLINK_BASE_PATH=/NestLink NEXT_PUBLIC_BASE_PATH=/NestLink NEXT_PUBLIC_API_URL=http://localhost:9999 npm run build`
  (nota: hace falta también `NEXT_PUBLIC_BASE_PATH=/NestLink` para el runtime estático).
- Deploy: `configure-pages → upload-pages-artifact (frontend/out) → deploy-pages`.

## 3. Preview local correcto (⚠️ no uses `npx serve -s out`)
`serve -s` reescribe `/NestLink/_next/*.js` y `/NestLink/maps/*.json` a `index.html` (200 text/html) → la app se rompe.
La forma fiel (idéntica a Pages) es servir el PADRE con `out/` dentro de una subcarpeta `NestLink/`:
```
mkdir -p /tmp/pages_preview/NestLink && cp -R frontend/out/* /tmp/pages_preview/NestLink/
cd /tmp/pages_preview && npx serve -l 4100          # http://localhost:4100/NestLink/
```
Verificar: GET /NestLink/ → 200; /NestLink/_next/*.js → 200 JS; /NestLink/maps/realistic_layout.json → 200 JSON; OCR confirma badge "Demo local" + planta Realistic.

## 4. Modo offline en estático
Con Pages, la app entra **directo al DemoEngine** (`IS_STATIC_PAGES` evita health-check/WS):
planta Realistic embebida como fallback local (`/NestLink/maps/realistic_layout.json`), 4 AMR, KANBAN, KPIs, controles (Derrame/Despeje/Pico/Reset/+5/−5).
