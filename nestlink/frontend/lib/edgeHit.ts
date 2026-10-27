import type { LayoutEdge, PlantLayout } from "./types";

export function edgeKey(a: string, b: string) {
  return a < b ? `${a}-${b}` : `${b}-${a}`;
}

/** Distancia de un punto a un segmento (coords layout) */
export function distToSegment(
  px: number,
  py: number,
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len2 = dx * dx + dy * dy;
  if (len2 === 0) return Math.hypot(px - x1, py - y1);
  let t = ((px - x1) * dx + (py - y1) * dy) / len2;
  t = Math.max(0, Math.min(1, t));
  const projX = x1 + t * dx;
  const projY = y1 + t * dy;
  return Math.hypot(px - projX, py - projY);
}

export interface EdgeHit {
  from: string;
  to: string;
  distance: number;
}

/** Encuentra la arista más cercana al punto (coords layout) */
export function findEdgeAtPoint(
  layout: PlantLayout,
  lx: number,
  ly: number,
  threshold = 12
): EdgeHit | null {
  let best: EdgeHit | null = null;

  layout.edges.forEach((e: LayoutEdge) => {
    const na = layout.nodes.find((n) => n.id === e.from);
    const nb = layout.nodes.find((n) => n.id === e.to);
    if (!na || !nb) return;
    const d = distToSegment(lx, ly, na.x, na.y, nb.x, nb.y);
    if (d <= threshold && (!best || d < best.distance)) {
      best = { from: e.from, to: e.to, distance: d };
    }
  });

  return best;
}

/** Encuentra la arista más cercana en espacio de pantalla (canvas pixels) */
export function findEdgeAtScreenPoint(
  layout: PlantLayout,
  sx: number,
  sy: number,
  toScreen: (x: number, y: number) => { x: number; y: number },
  thresholdPx = 18
): EdgeHit | null {
  let best: EdgeHit | null = null;

  layout.edges.forEach((e: LayoutEdge) => {
    const na = layout.nodes.find((n) => n.id === e.from);
    const nb = layout.nodes.find((n) => n.id === e.to);
    if (!na || !nb) return;
    const sa = toScreen(na.x, na.y);
    const sb = toScreen(nb.x, nb.y);
    const d = distToSegment(sx, sy, sa.x, sa.y, sb.x, sb.y);
    if (d <= thresholdPx && (!best || d < best.distance)) {
      best = { from: e.from, to: e.to, distance: d };
    }
  });

  return best;
}
