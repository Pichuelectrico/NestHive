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
  realistic: `${BASE_PATH}/maps/realistic_layout.json`,
  espol_fusion: `${BASE_PATH}/maps/espol_fusion.json`,
};

export const DEFAULT_PLANT_ID = "espol_fusion";
export const DEFAULT_PLANT_NAME = "Planta ESPOL Fusion";

export const FLEET_PRESENTATION = {
  AGV_IDS: ["AMR_01", "AMR_02", "AMR_03", "AMR_05", "AMR_06"],
  AMR_IDS: ["AMR_04", "AMR_05"],
  AGV_COLOR: "#E4032E",
  AMR_COLOR: "#2563EB",
  TRANSPORT_AGV_IDS: ["AMR_03"],
  TRANSPORT_AGV_COLOR: "#2563EB",
  NAME_OVERRIDES: { AMR_01: "AGV 1 · Nestlé", AMR_02: "AGV 2 · Maggi", AMR_03: "AGV 3 · Savoy", AMR_06: "AGV 6 · Expedición", AMR_04: "AMR 4 · Apoyo", AMR_05: "AMR 5 · Apoyo" } as Record<string, string>,
} as const;
export function tipoDeAmr(id: string): "AGV" | "AMR" { return (FLEET_PRESENTATION.AMR_IDS as readonly string[]).includes(id) ? "AMR" : "AGV"; }
export function colorDeFlota(id: string, plantId?: string): string {
  if (plantId === "espol_fusion") {
    return (FLEET_PRESENTATION.TRANSPORT_AGV_IDS as readonly string[]).includes(id)
      ? FLEET_PRESENTATION.TRANSPORT_AGV_COLOR
      : FLEET_PRESENTATION.AGV_COLOR;
  }
  return tipoDeAmr(id) === "AMR" ? FLEET_PRESENTATION.AMR_COLOR : FLEET_PRESENTATION.AGV_COLOR;
}

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
};

/** Mapa visual v2 (estilo New_map.png) para espol_fusion. Default ON; rollback en caliente
 *  con `?visual=v1` en la URL (sin rebuild) o en build con NEXT_PUBLIC_VISUAL_V2=0. */
export const VISUAL_V2 = (process.env.NEXT_PUBLIC_VISUAL_V2 ?? "1").trim() !== "0";
export const VISUAL_V2_DEFAULT = VISUAL_V2;
export const VISUAL_V2_PLANTS = ["espol_fusion"];

export function isVisualV2Enabled(plantId?: string): boolean {
  if (plantId && !VISUAL_V2_PLANTS.includes(plantId)) return false;
  if (typeof window !== "undefined") {
    const q = new URLSearchParams(window.location.search).get("visual");
    if (q === "v1") return false;
    if (q === "v2") return true;
  }
  return VISUAL_V2_DEFAULT;
}
