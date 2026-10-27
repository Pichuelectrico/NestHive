import type { AMRRenderState, PlantLayout } from "@/lib/types";

/** Proyecta un punto sobre el segmento [a → b], clamped a los extremos. */
export function projectOntoSegment(
  px: number,
  py: number,
  ax: number,
  ay: number,
  bx: number,
  by: number
): { x: number; y: number } {
  const dx = bx - ax;
  const dy = by - ay;
  const lenSq = dx * dx + dy * dy;
  if (lenSq < 1e-6) return { x: ax, y: ay };
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / lenSq));
  return { x: ax + t * dx, y: ay + t * dy };
}

/**
 * Ancla visual del AMR sobre la arista activa (path[0]).
 * El LERP puede desviarse ~1–2 px de la centerline; proyectamos sobre el tramo layout.
 */
export function getAmrAnchor(
  amr: Pick<AMRRenderState, "renderX" | "renderY" | "path">,
  layout: PlantLayout
): { x: number; y: number } {
  const px = amr.renderX;
  const py = amr.renderY;
  if (amr.path.length === 0) return { x: px, y: py };

  const nextId = amr.path[0];
  const next = layout.nodes.find((n) => n.id === nextId);
  if (!next) return { x: px, y: py };

  let bestDist = Infinity;
  let best = { x: px, y: py };

  for (const e of layout.edges) {
    const fromId = e.to === nextId ? e.from : e.from === nextId ? e.to : null;
    if (!fromId) continue;
    const from = layout.nodes.find((n) => n.id === fromId);
    if (!from) continue;
    const proj = projectOntoSegment(px, py, from.x, from.y, next.x, next.y);
    const dist = Math.hypot(proj.x - px, proj.y - py);
    if (dist < bestDist) {
      bestDist = dist;
      best = proj;
    }
  }

  return best;
}
