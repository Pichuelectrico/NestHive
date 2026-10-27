import type { AMRRenderState, Mission, PlantLayout } from "./types";

export interface AmrCargoVisual {
  cargoEmoji: string;
  routeColor: string;
}

function nodeTypeAt(
  layout: PlantLayout,
  nodeId: string | undefined
): string | undefined {
  if (!nodeId) return undefined;
  return layout.nodes.find((n) => n.id === nodeId)?.type;
}

/** Resuelve emoji de carga y color de ruta: misión por id → fallback path/layout. */
export function resolveAmrCargoVisual(
  amr: AMRRenderState,
  layout: PlantLayout,
  missionById: Map<string, Mission>
): AmrCargoVisual {
  if (amr.estado === "CHARGING") {
    return { cargoEmoji: "⚡", routeColor: "#f59e0b" };
  }

  const mission =
    typeof amr.tarea_asignada === "string" && amr.tarea_asignada
      ? missionById.get(amr.tarea_asignada)
      : undefined;

  if (mission) {
    switch (mission.tipo) {
      case "RECHARGE":
        return { cargoEmoji: "⚡", routeColor: "#f59e0b" };
      case "SUPPLY_REQUEST":
        return { cargoEmoji: "📦", routeColor: "#f59e0b" };
      case "PICKUP_PT":
        return { cargoEmoji: "🏭", routeColor: "#a78bfa" };
      case "EXPEDITION":
        return { cargoEmoji: "🏭", routeColor: "#a78bfa" };
      case "EXPORT":
        // Entrega EXCLUSIVA al muro (ruta rosada): el paquete ya salió del OUT (emoji apagado) y viaja a la pared
        return { cargoEmoji: "🚛", routeColor: "#10b981" };
      case "RELOCATION":
        return { cargoEmoji: "🚚", routeColor: "#4a90b8" };
      default:
        break;
    }
  }

  const destId = amr.path.at(-1);
  const destType = nodeTypeAt(layout, destId);

  if (destType === "empacadora") {
    return { cargoEmoji: "📦", routeColor: "#f59e0b" };
  }
  if (destType === "almacen") {
    return { cargoEmoji: "🏭", routeColor: "#a78bfa" };
  }
  if (destType === "carga") {
    return { cargoEmoji: "⚡", routeColor: "#f59e0b" };
  }

  if (!amr.tarea_asignada && amr.path.length === 0) {
    return { cargoEmoji: "🚚", routeColor: "#4a90b8" };
  }

  if (amr.estado === "MOVING_TO_PICKUP") {
    return { cargoEmoji: "🚚", routeColor: "#4a90b8" };
  }

  return { cargoEmoji: "📦", routeColor: "#4a90b8" };
}

export function getBatteryEmoji(amr: AMRRenderState): string {
  if (amr.estado === "CHARGING") return "⚡";
  if (amr.bateria <= 25) return "🪫";
  return "🔋";
}
