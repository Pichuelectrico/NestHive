import type { EstadoAMR } from "./types";

/** Colores de aro por estado AMR — semáforo del plan NestLink (NO cambiar en realistic) */
export const AMR_STATE_COLORS: Record<EstadoAMR, string> = {
  IDLE: "#8b949e",
  MOVING_TO_PICKUP: "#3fb950",
  MOVING_TO_DELIVERY: "#3fb950",
  LOADING: "#d29922",
  UNLOADING: "#d29922",
  WAITING_OBSTACLE: "#db6d28",
  REROUTING: "#388bfd",
  CHARGING: "#f85149",
  ERROR: "#f85149",
};

export const AMR_BODY_COLORS = [
  "#e85d04",
  "#2d6a4f",
  "#e63946",
  "#457b9d",
  "#6a4c93",
];

/** Rojo marca Nestlé — flota unificada en planta realistic */
export const NESTLE_FLEET_RED = "#E4032E";

export function getAmrColor(index: number, plantId?: string): string {
  if (plantId === "realistic") return NESTLE_FLEET_RED;
  return AMR_BODY_COLORS[index % AMR_BODY_COLORS.length];
}

export function priorityClass(prioridad: number): string {
  if (prioridad >= 10) return "border-l-red-500";
  if (prioridad >= 8) return "border-l-orange-500";
  if (prioridad >= 5) return "border-l-yellow-500";
  return "border-l-green-500";
}

export function priorityEmoji(prioridad: number): string {
  if (prioridad >= 10) return "🔴";
  if (prioridad >= 8) return "🟠";
  if (prioridad >= 5) return "🟡";
  return "🟢";
}
