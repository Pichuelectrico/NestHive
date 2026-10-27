/**
 * Configuración centralizada del frontend NestLink.
 *
 * NEXT_PUBLIC_* se incrusta en el bundle en BUILD (ver Dockerfile ARG).
 * Si la variable no está definida en el entorno de build, usamos localhost.
 */
const DEFAULT_API = "http://localhost:8000";

/** Subpath de despliegue estático (GitHub Pages). Override: NEXT_PUBLIC_BASE_PATH (ej. "/NestLink").
 *  Vacío en Docker/live → todas las rutas locales quedan en la raíz. */
export const BASE_PATH = (process.env.NEXT_PUBLIC_BASE_PATH ?? "").trim();

/** true cuando el bundle es para un despliegue estático (Pages): no hay backend →
 *  el front entra directo en modo offline (DemoEngine), sin esperar health-check. */
export const IS_STATIC_PAGES = BASE_PATH.length > 0;

/** URL base del backend FastAPI (REST). Override: NEXT_PUBLIC_API_URL */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.trim() || DEFAULT_API;

/** WebSocket de telemetría. Override: NEXT_PUBLIC_WS_URL */
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL?.trim() ||
  API_BASE.replace(/^http/, "ws") + "/ws";

export const BACKEND_TIMEOUT_MS = 1500;

/**
 * Fallbacks locales por planta (modo offline/estático; mismo esquema que el backend).
 * realistic_layout.json se genera desde la respuesta real de /api/v1/layout?plant=realistic.
 * Se prefijan con BASE_PATH en runtime para que en Pages cargue /NestLink/maps/... y en
 * local/raíz siga siendo /maps/... (docker/live: BASE_PATH="").
 */
export const LAYOUT_FALLBACK_PATHS: Record<string, string> = {
  quito: `${BASE_PATH}/maps/plant_layout.json`,
  realistic: `${BASE_PATH}/maps/realistic_layout.json`,
  espol_fusion: `${BASE_PATH}/maps/espol_fusion.json`,
};

export const DEFAULT_PLANT_ID = "realistic";
export const DEFAULT_PLANT_NAME = "Planta Realistic";

export const CANVAS_W = 800;
export const CANVAS_H = 500;

/** Access Point Wi-Fi (capa demo de conectividad). Coords en el sistema del layout de la planta. */
export interface WifiAp {
  id: string;
  x: number;
  y: number;
}

/**
 * APs industriales tipo — 1 AP cada 2–3 pasillos, cabeceo al pasillo
 * (tasksR/wifi_industrial_fase2.md). Solo visual local; no hay API.
 */
export const WIFI_APS_BY_PLANT: Record<string, WifiAp[]> = {
  espol_fusion: [
    { id: "AP_E1", x: 180, y: 120 }, { id: "AP_E2", x: 420, y: 120 },
    { id: "AP_E3", x: 680, y: 220 }, { id: "AP_E4", x: 820, y: 420 },
  ],
  // Canvas 1000×600 — pasillos X_T (y≈55), X_M (x≈400), racks X_R (x≈740), OUT (x≈530)
  realistic: [
    { id: "AP_T1", x: 200, y: 55 },
    { id: "AP_T2", x: 360, y: 55 },
    { id: "AP_T3", x: 520, y: 55 },
    { id: "AP_T4", x: 680, y: 55 },
    { id: "AP_T5", x: 820, y: 55 },
    { id: "AP_M1", x: 400, y: 160 },
    { id: "AP_M2", x: 400, y: 300 },
    { id: "AP_R1", x: 740, y: 160 },
    { id: "AP_R2", x: 740, y: 320 },
    { id: "AP_OUT", x: 530, y: 360 },
  ],
  // Canvas 800×500 — cobertura tipo sobre el mapa clásico
  quito: [
    { id: "AP_Q1", x: 160, y: 80 },
    { id: "AP_Q2", x: 360, y: 80 },
    { id: "AP_Q3", x: 560, y: 80 },
    { id: "AP_Q4", x: 280, y: 250 },
    { id: "AP_Q5", x: 480, y: 250 },
    { id: "AP_Q6", x: 400, y: 400 },
  ],
};
