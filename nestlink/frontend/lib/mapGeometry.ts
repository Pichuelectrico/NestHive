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

/** Posición interpolada real del AMR recibida del simulador. */
export function getAmrAnchor(
  amr: Pick<AMRRenderState, "renderX" | "renderY" | "path">,
  _layout: PlantLayout
): { x: number; y: number } {
  return { x: amr.renderX, y: amr.renderY };
}
