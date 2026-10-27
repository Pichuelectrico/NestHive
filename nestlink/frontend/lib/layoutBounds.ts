import type { PlantLayout } from "./types";

export interface LayoutBounds {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
  width: number;
  height: number;
}

const PADDING = 48;

/** Bounds del contenido del mapa (canvas + nodos) para fit/centrado */
export function getLayoutBounds(layout: PlantLayout): LayoutBounds {
  let minX = 0;
  let minY = 0;
  let maxX = layout.canvas?.w ?? 800;
  let maxY = layout.canvas?.h ?? 500;

  layout.nodes.forEach((n) => {
    minX = Math.min(minX, n.x - PADDING);
    minY = Math.min(minY, n.y - PADDING);
    maxX = Math.max(maxX, n.x + PADDING);
    maxY = Math.max(maxY, n.y + PADDING);
  });

  return {
    minX,
    minY,
    maxX,
    maxY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

export function nearestNodeId(
  layout: PlantLayout,
  x: number,
  y: number
): string {
  let bestId = "";
  let bestD = Infinity;
  layout.nodes.forEach((n) => {
    const d = Math.hypot(n.x - x, n.y - y);
    if (d < bestD) {
      bestD = d;
      bestId = n.id;
    }
  });
  return bestId;
}
