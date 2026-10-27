import {
  API_BASE,
  BACKEND_TIMEOUT_MS,
  DEFAULT_PLANT_ID,
  DEFAULT_PLANT_NAME,
  LAYOUT_FALLBACK_PATHS,
} from "./config";
import type { Mission, PlantInfo, PlantLayout, SimulationSnapshot } from "./types";

async function fetchWithTimeout(
  url: string,
  options?: RequestInit,
  timeout = BACKEND_TIMEOUT_MS
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchLayout(plantId?: string): Promise<PlantLayout> {
  const plant = plantId ?? DEFAULT_PLANT_ID;
  const qs = plant ? `?plant=${encodeURIComponent(plant)}` : "";

  // 1) Backend real con timeout
  try {
    const res = await fetchWithTimeout(`${API_BASE}/api/v1/layout${qs}`);
    if (res.ok) {
      const json = await res.json();
      if (json && Array.isArray(json.nodes)) return json as PlantLayout;
    }
  } catch {
    // caer al fallback local solo para planta default
  }

  // 2) Fallback local (modo offline/estático) — hay un archivo por planta en /public/maps/
  //    (quito y realistic; mismo esquema que responde el backend).
  const fallbackPath = LAYOUT_FALLBACK_PATHS[plant];
  if (fallbackPath) {
    try {
      const local = await fetchWithTimeout(fallbackPath, {}, 3000);
      if (local.ok) return (await local.json()) as PlantLayout;
    } catch {
      // caer al modo sin mapa
    }
  }

  throw new Error(
    `No se pudo cargar el layout para planta "${plant}" (backend ni fallback local)`
  );
}

export async function fetchPlants(): Promise<PlantInfo[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/api/v1/plants`);
    if (res.ok) {
      const data = await res.json();
      // El backend devuelve {plants:[...]}; aceptamos también array plano por robustez
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.plants)
          ? data.plants
          : null;
      if (list && list.length) return list as PlantInfo[];
    }
  } catch {
    // fallback local
  }
  return [
    {
      id: DEFAULT_PLANT_ID,
      nombre: DEFAULT_PLANT_NAME,
      layout_url: "",
    },
  ];
}

export async function selectPlant(plantId: string) {
  const res = await fetch(`${API_BASE}/api/v1/sim/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plant: plantId }),
  });
  if (!res.ok) throw new Error("select plant failed");
  return res.json();
}

export async function fetchMissions(): Promise<Mission[]> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/api/v1/missions`);
    if (res.ok) return res.json();
  } catch {
    // offline — caller uses demo missions
  }
  return [];
}

export async function postEmergencyPickup(line: string) {
  const res = await fetch(`${API_BASE}/api/v1/emergency/pickup?line=${encodeURIComponent(line)}`, { method: "POST" });
  if (!res.ok) throw new Error("emergency pickup failed");
  return res.json();
}

export async function blockEdge(from: string, to: string, tipo = "SPILL") {
  const res = await fetch(`${API_BASE}/api/v1/obstacles/block`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from, to, tipo }),
  });
  if (!res.ok) throw new Error("block failed");
  return res.json();
}

export async function unblockEdge(from: string, to: string) {
  const res = await fetch(`${API_BASE}/api/v1/obstacles/unblock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from, to }),
  });
  if (!res.ok) throw new Error("unblock failed");
  return res.json();
}

export async function injectPeak(lineId: string, drainPct = 30) {
  const res = await fetch(`${API_BASE}/api/v1/sim/peak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ line_id: lineId, drain_pct: drainPct }),
  });
  if (!res.ok) throw new Error("peak failed");
  return res.json();
}

export async function simulateLowBattery(amrId: string) {
  const res = await fetch(`${API_BASE}/api/v1/sim/low_battery`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amr_id: amrId }),
  });
  if (!res.ok) throw new Error("low_battery failed");
  return res.json();
}

export interface RefillResponse {
  status: string;
  target_pct: number;
  line_id?: string | null;
  lines: string[];
}

export interface ResetMissionsResponse {
  status: string;
  missions_clearadas: number;
  activas: number;
}

export interface AdjustMissionsResponse {
  status: string;
  delta: number;
  pendientes: number;
}

export async function resetMissions(): Promise<ResetMissionsResponse> {
  const res = await fetch(`${API_BASE}/api/v1/sim/reset_missions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) throw new Error("reset_missions failed");
  const data = await res.json();
  return {
    status: data.status ?? "ok",
    missions_clearadas: data.missions_clearadas ?? 0,
    activas: data.activas ?? 0,
  };
}

export async function adjustMissions(delta: number): Promise<AdjustMissionsResponse> {
  if (delta === 0 || delta % 5 !== 0) {
    throw new Error("delta must be a non-zero multiple of 5");
  }
  const res = await fetch(`${API_BASE}/api/v1/sim/adjust_missions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ delta }),
  });
  if (!res.ok) throw new Error("adjust_missions failed");
  const data = await res.json();
  return {
    status: data.status ?? "ok",
    delta: data.delta ?? delta,
    pendientes: data.pendientes ?? 0,
  };
}

export async function refillLine(
  lineId?: string | null,
  targetPct = 80
): Promise<RefillResponse> {
  const body: { target_pct: number; line_id?: string } = {
    target_pct: targetPct,
  };
  if (lineId) body.line_id = lineId;

  const res = await fetch(`${API_BASE}/api/v1/sim/refill`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error("refill failed");
  const data = await res.json();
  return {
    status: data.status ?? "refill_scheduled",
    target_pct: data.target_pct ?? targetPct,
    line_id: data.line_id ?? lineId,
    lines: Array.isArray(data.lines) ? data.lines : lineId ? [lineId] : [],
  };
}

export function parseSnapshot(raw: unknown): SimulationSnapshot | null {
  if (!raw || typeof raw !== "object") return null;
  const s = raw as SimulationSnapshot;
  if (!Array.isArray(s.amrs) || !Array.isArray(s.lines)) return null;
  return s;
}

/** Preguntas prefijadas del asistente de flota (NestHive). */
export interface ChatAskItem {
  id: number;
  question: string;
}

export interface ChatAskResponse {
  answer: string;
  data: Record<string, unknown>;
  ts: string | number;
}

export interface HourlyReport {
  event?: string;
  status?: string;
  sim_hour?: number;
  ts?: string | number;
  movements?: number;
  pallets_delivered?: number;
  incidents?: number;
  delta?: Record<string, number>;
  kpis?: Record<string, unknown>;
  [key: string]: unknown;
}

/** Preguntas locales si el motor de chat aún no responde. */
export const FALLBACK_CHAT_ASKS: ChatAskItem[] = [
  { id: 1, question: "¿Cuál es el estado de la flota?" },
  { id: 2, question: "¿Cómo están las baterías?" },
  { id: 3, question: "¿Qué misiones están en curso?" },
  { id: 4, question: "¿Cuál es el cuello de botella ahora mismo?" },
  { id: 5, question: "¿Cuál es la próxima parada de línea por stock bajo?" },
  { id: 6, question: "¿Cómo va el turno?" },
  { id: 7, question: "¿Qué incidencias ocurrieron en la última hora?" },
  { id: 8, question: "¿Cuál es la estrategia actual del orquestador?" },
  { id: 9, question: "¿Qué misiones se completaron en la última hora?" },
  { id: 10, question: "¿Qué riesgo debo vigilar ahora?" },
];

export async function fetchChatAsks(): Promise<ChatAskItem[] | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/api/v1/chat/asks`);
    if (!res.ok) return null;
    const data = await res.json();
    if (Array.isArray(data) && data.length) {
      if (typeof data[0] === "string") {
        return (data as string[]).map((q, i) => ({ id: i + 1, question: q }));
      }
      return (data as ChatAskItem[]).filter(
        (x) => x && typeof x.question === "string"
      );
    }
  } catch {
    // motor no disponible
  }
  return null;
}

export async function askChat(q: string): Promise<ChatAskResponse | null> {
  try {
    const res = await fetchWithTimeout(
      `${API_BASE}/api/v1/chat/ask?q=${encodeURIComponent(q)}`,
      {},
      4000
    );
    if (!res.ok) return null;
    const data = await res.json();
    if (!data || typeof data.answer !== "string") return null;
    return {
      answer: data.answer,
      data:
        data.data && typeof data.data === "object"
          ? (data.data as Record<string, unknown>)
          : {},
      ts: data.ts ?? Date.now(),
    };
  } catch {
    return null;
  }
}

export async function fetchHourlyReport(): Promise<HourlyReport | null> {
  try {
    const res = await fetchWithTimeout(`${API_BASE}/api/v1/chat/report`);
    if (!res.ok) return null;
    const data = await res.json();
    if (!data || typeof data !== "object") return null;
    return data as HourlyReport;
  } catch {
    return null;
  }
}

/** true si el mensaje WS es un reporte horario (no un snapshot de simulación). */
export function parseHourlyReportEvent(raw: unknown): HourlyReport | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as HourlyReport;
  if (o.event === "hourly_report_ready") return o;
  return null;
}
