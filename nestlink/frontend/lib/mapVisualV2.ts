/**
 * Renderer visual v2 de espol_fusion (estilo New_map.png).
 *
 * La geometría visible sale de los nodos y aristas recibidos en layout.
 * Del PNG (extracción CV de Codex, espol_fusion_visual.json) se toman paleta y semántica.
 */
import type { LayoutEdge, LayoutNode, PlantLayout } from "@/lib/types";

/** Paleta muestreada del New_map.png (new_map_markers.json / espol_fusion_visual.json). */
export const V2_COLORS = {
  morado: "#b96bd4",
  verde: "#6dcc62",
  azul: "#536ff0",
  amarillo: "#ffc45a",
  cafe: "#7a3e0b",
  naranja: "#ff6b21",
  rojo: "#ff302c",
  fondo: "#fbf8f1",
  corredor: "#e9e3d7",
  linea: "#2b2118",
  muro: "#a8a29e",
  texto: "#5b3918",
} as const;

type ToScreen = (x: number, y: number) => { x: number; y: number };

const CORRIDOR_W = 9;
function isExpeditionEdge(e: LayoutEdge, nodes: Map<string, LayoutNode>): boolean {
  const domain = (e as LayoutEdge & { domain?: string }).domain;
  if (domain === "AMR" || domain === "EXPEDITION") return true;
  if (e.from.startsWith("TRANSPORTE") || e.to.startsWith("TRANSPORTE")) return true;
  // Los accesos reales al perímetro izquierdo nacen fuera de la planta.
  const from = nodes.get(e.from);
  const to = nodes.get(e.to);
  return !!from && !!to && (from.x < 50 || to.x < 50);
}

function isPaletMarker(id: string): boolean {
  return /^PALET_\d+$/.test(id);
}

/** Aristas visibles únicas; el grafo incluye pares inversos para aristas bidireccionales. */
function visibleCorridorEdges(layout: PlantLayout): LayoutEdge[] {
  const seen = new Set<string>();
  const nodes = new Map(layout.nodes.map((node) => [node.id, node]));
  return layout.edges.filter((edge) => {
    if (isExpeditionEdge(edge, nodes)) return false;
    const from = nodes.get(edge.from);
    const to = nodes.get(edge.to);
    if (!from || !to || Math.hypot(from.x - to.x, from.y - to.y) < 1e-6) return false;
    const key = edge.direction?.toLowerCase() === "bi"
      ? [edge.from, edge.to].sort().join("|")
      : `${edge.from}|${edge.to}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

type BluePoint = { id: string; x: number; y: number };

function numberedBluePoints(layout: PlantLayout): BluePoint[] {
  const hasCanonicalIds = layout.nodes.some((node) => /^B\d+$/.test(node.id));
  return layout.nodes
    .filter((node) => node.type === "cruce" && (!hasCanonicalIds || /^B\d+$/.test(node.id)))
    .filter((node) => node.id !== "B34")
    .map((node) => ({ id: node.id, x: node.x, y: node.y }));
}

function drawBluePointNumber(ctx: CanvasRenderingContext2D, point: BluePoint, toScreen: ToScreen, scale: number) {
  if (!/^B\d+$/.test(point.id)) return;
  const s = toScreen(point.x, point.y);
  label(ctx, point.id, s.x + 5 * scale, s.y - 5 * scale, 4.8 * scale, "#2446b8");
}

function bbox(nodes: LayoutNode[]) {
  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  return {
    minX: Math.min(...xs),
    minY: Math.min(...ys),
    maxX: Math.max(...xs),
    maxY: Math.max(...ys),
  };
}

function arrowHead(
  ctx: CanvasRenderingContext2D,
  at: { x: number; y: number },
  angle: number,
  size: number,
  color: string
) {
  ctx.save();
  ctx.translate(at.x, at.y);
  ctx.rotate(angle);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(size, 0);
  ctx.lineTo(-size * 0.7, size * 0.6);
  ctx.lineTo(-size * 0.7, -size * 0.6);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

/** roundRect con respaldo a rect: Safari<16 / Chrome<99 no lo implementan y lanzarían. */
function roundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  if (typeof ctx.roundRect === "function") ctx.roundRect(x, y, w, h, r);
  else ctx.rect(x, y, w, h);
}

function label(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  px: number,
  color: string = V2_COLORS.texto
) {
  ctx.save();
  ctx.font = `600 ${px}px sans-serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.strokeStyle = "rgba(251,248,241,0.92)";
  ctx.lineWidth = Math.max(2, px / 3.5);
  ctx.strokeText(text, x, y);
  ctx.fillStyle = color;
  ctx.fillText(text, x, y);
  ctx.restore();
}

/** Zona semántica: rect redondeado relleno suave + borde punteado del color del marcador. */
function zoneAround(
  ctx: CanvasRenderingContext2D,
  nodes: LayoutNode[],
  pad: number,
  color: string,
  toScreen: ToScreen,
  scale: number
) {
  if (nodes.length === 0) return;
  const b = bbox(nodes);
  const tl = toScreen(b.minX - pad, b.minY - pad);
  const br = toScreen(b.maxX + pad, b.maxY + pad);
  const w = br.x - tl.x;
  const h = br.y - tl.y;
  ctx.save();
  ctx.fillStyle = color + "1f";
  ctx.strokeStyle = color + "b3";
  ctx.lineWidth = 1.2;
  ctx.setLineDash([5 * scale, 3 * scale]);
  ctx.beginPath();
  roundedRect(ctx, tl.x, tl.y, w, h, 6 * scale);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

/** Zonas semánticas del plano: nodos que encierran, margen, color y título. */
function semanticZones(layout: PlantLayout) {
  return [
    { nodes: layout.nodes.filter((n) => isPaletMarker(n.id)), pad: 8, color: V2_COLORS.morado, title: "Paletizaje" },
    { nodes: layout.nodes.filter((n) => n.type === "carga"), pad: 9, color: V2_COLORS.verde, title: "Carga" },
    {
      nodes: layout.nodes.filter((n) => n.id.startsWith("WH_MP_") || n.id.startsWith("FUENTE_INSUMOS")),
      pad: 9,
      color: V2_COLORS.cafe,
      title: "Insumos",
    },
  ].filter((z) => z.nodes.length > 0);
}

/** Títulos de zona: se pintan al final para que los corredores no los tapen. */
export function drawVisualV2ZoneTitles(
  ctx: CanvasRenderingContext2D,
  layout: PlantLayout,
  toScreen: ToScreen,
  scale: number
) {
  for (const z of semanticZones(layout)) {
    const b = bbox(z.nodes);
    const tl = toScreen(b.minX - z.pad, b.minY - z.pad);
    const br = toScreen(b.maxX + z.pad, b.maxY + z.pad);
    label(ctx, z.title, (tl.x + br.x) / 2, tl.y - 6 * scale, 7 * scale, z.color);
  }

  // "Punto de Entrega": como en el PNG, a la derecha de la 2.ª fila de puntos morados
  const palet = layout.nodes.filter((n) => isPaletMarker(n.id));
  const rows: LayoutNode[][] = [];
  for (const n of [...palet].sort((a, b) => a.y - b.y)) {
    const row = rows.find((r) => Math.abs(r[0].y - n.y) < 8);
    if (row) row.push(n);
    else rows.push([n]);
  }
  // Anchor explicitly to the rightmost node of the second purple row (PALET_10)
  // so the label remains stable after graph-space marker relocation.
  const target = palet.find((n) => n.id === "PALET_10") ?? rows[1]?.[rows[1].length - 1] ?? rows[0]?.[rows[0].length - 1];
  if (target) {
    const right = target;
    const s = toScreen(right.x, right.y);
    ctx.save();
    ctx.textAlign = "left";
    ctx.font = `600 ${6.5 * scale}px sans-serif`;
    const text = "Punto de Entrega";
    ctx.strokeStyle = "rgba(251,248,241,0.92)";
    ctx.lineWidth = Math.max(2, (6.5 * scale) / 3.5);
    ctx.textBaseline = "middle";
    ctx.strokeText(text, s.x + 10 * scale, s.y);
    ctx.fillStyle = V2_COLORS.texto;
    ctx.fillText(text, s.x + 10 * scale, s.y);
    ctx.restore();
  }
}

/**
 * Capa inferior: fondo, muros punteados, zonas semánticas y corredores (aristas reales
 * como bandas anchas + línea central + flechas de sentido). Se dibuja ANTES del bucle
 * de aristas del renderer (que en v2 solo pinta bloqueos/hover/selección).
 */
export function drawVisualV2Underlay(
  ctx: CanvasRenderingContext2D,
  layout: PlantLayout,
  toScreen: ToScreen,
  scale: number
) {
  const nodeById = new Map(layout.nodes.map((n) => [n.id, n]));
  // El perímetro de la planta excluye el transporte externo en x=20.
  const tl = toScreen(50, 25);
  const br = toScreen(950, 580);
  ctx.fillStyle = V2_COLORS.fondo;
  ctx.fillRect(tl.x, tl.y, br.x - tl.x, br.y - tl.y);

  // Muro perimetral punteado gris (estilo New_map.png)
  ctx.save();
  ctx.strokeStyle = V2_COLORS.muro;
  ctx.lineWidth = Math.max(1.5, 1.6 * scale);
  ctx.setLineDash([3 * scale, 3 * scale]);
  ctx.strokeRect(tl.x, tl.y, br.x - tl.x, br.y - tl.y);
  ctx.restore();

  // Paredes físicas recibidas del API.
  ctx.save();
  ctx.strokeStyle = V2_COLORS.muro;
  ctx.lineWidth = Math.max(1.5, 1.6 * scale);
  ctx.setLineDash([3 * scale, 3 * scale]);
  for (const wall of layout.walls ?? []) {
    const a = toScreen(wall.x, wall.y + wall.h / 2);
    const c = toScreen(wall.x + wall.w, wall.y + wall.h / 2);
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(c.x, c.y);
    ctx.stroke();
  }
  ctx.restore();

  // Zonas semánticas alrededor de los nodos reales
  for (const z of semanticZones(layout)) zoneAround(ctx, z.nodes, z.pad, z.color, toScreen, scale);

  // Cada tramo corresponde a una arista real del layout, incluidas las diagonales.
  const corridorEdges = visibleCorridorEdges(layout);
  ctx.save();
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = V2_COLORS.corredor;
  ctx.lineWidth = CORRIDOR_W * scale;
  ctx.beginPath();
  for (const e of corridorEdges) {
    const a = nodeById.get(e.from);
    const c = nodeById.get(e.to);
    if (!a || !c) continue;
    const sa = toScreen(a.x, a.y);
    const sc = toScreen(c.x, c.y);
    ctx.moveTo(sa.x, sa.y);
    ctx.lineTo(sc.x, sc.y);
  }

  ctx.stroke();

  // Línea central negra fina (las flechas del plano)
  ctx.strokeStyle = V2_COLORS.linea;
  ctx.lineWidth = Math.max(1, 1.1 * scale);
  ctx.beginPath();
  for (const e of corridorEdges) {
    const a = nodeById.get(e.from);
    const c = nodeById.get(e.to);
    if (!a || !c) continue;
    const sa = toScreen(a.x, a.y);
    const sc = toScreen(c.x, c.y);
    ctx.moveTo(sa.x, sa.y);
    ctx.lineTo(sc.x, sc.y);
  }
  ctx.stroke();
  ctx.restore();

  // Puntas de flecha: sentido en aristas one-way, doble punta en las bidireccionales
  for (const e of corridorEdges) {
    const a = nodeById.get(e.from);
    const c = nodeById.get(e.to);
    if (!a || !c) continue;
    const sa = toScreen(a.x, a.y);
    const sc = toScreen(c.x, c.y);
    const len = Math.hypot(sc.x - sa.x, sc.y - sa.y);
    if (len < 14 * scale) continue;
    const ang = Math.atan2(sc.y - sa.y, sc.x - sa.x);
    const size = Math.max(3, 3.4 * scale);
    const back = 7 * scale;
    const tip = { x: sc.x - Math.cos(ang) * back, y: sc.y - Math.sin(ang) * back };
    arrowHead(ctx, tip, ang, size, V2_COLORS.linea);
    if ((e.direction || "bi").toLowerCase() === "bi") {
      const tail = { x: sa.x + Math.cos(ang) * back, y: sa.y + Math.sin(ang) * back };
      arrowHead(ctx, tail, ang + Math.PI, size, V2_COLORS.linea);
    }
  }

  // Transporte externo: aristas reales hacia el nodo TRANSPORTE.
  ctx.save();
  ctx.strokeStyle = V2_COLORS.rojo;
  ctx.globalAlpha = 0.5;
  ctx.lineWidth = Math.max(1, 1.1 * scale);
  const seenTransport = new Set<string>();
  for (const e of layout.edges.filter((edge) => isExpeditionEdge(edge, nodeById))) {
    const a = nodeById.get(e.from);
    const c = nodeById.get(e.to);
    if (!a || !c || Math.hypot(a.x - c.x, a.y - c.y) < 1e-6) continue;
    const key = [e.from, e.to].sort().join("|");
    if (seenTransport.has(key)) continue;
    seenTransport.add(key);
    const sa = toScreen(a.x, a.y);
    const sc = toScreen(c.x, c.y);
    ctx.beginPath();
    ctx.moveTo(sa.x, sa.y);
    ctx.lineTo(sc.x, sc.y);
    ctx.stroke();
    const ang = Math.atan2(sc.y - sa.y, sc.x - sa.x);
    const back = 7 * scale;
    arrowHead(ctx, { x: sc.x - Math.cos(ang) * back, y: sc.y - Math.sin(ang) * back }, ang, 3.4 * scale, V2_COLORS.rojo);
    if ((e.direction || "bi").toLowerCase() === "bi") {
      arrowHead(ctx, { x: sa.x + Math.cos(ang) * back, y: sa.y + Math.sin(ang) * back }, ang + Math.PI, 3.4 * scale, V2_COLORS.rojo);
    }
  }
  ctx.restore();
}

/** Etiqueta corta de marcador: INSUMO_P1 → P1, RECO_R2 → R2. */
function markerLabel(n: LayoutNode): string | null {
  const m = n.id.match(/^(?:INSUMO_|RECO_)([PR]\d+)$/);
  return m ? m[1] : null;
}

/**
 * Capa de nodos v2: puntos azules de redireccionamiento, marcadores semánticos con el color
 * del plano y glifos sobrios para almacenes/líneas. Siempre en la posición REAL del nodo.
 */
export function drawVisualV2Nodes(
  ctx: CanvasRenderingContext2D,
  layout: PlantLayout,
  toScreen: ToScreen,
  scale: number
) {
  const bluePoints = numberedBluePoints(layout);
  for (const n of layout.nodes) {
    const s = toScreen(n.x, n.y);
    const dot = (r: number, color: string) => {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(s.x, s.y, r * scale, 0, Math.PI * 2);
      ctx.fill();
    };

    if (n.id.startsWith("TRANSPORTE")) {
      const r = 15 * scale;
      const g = ctx.createLinearGradient(s.x - r, s.y, s.x + r, s.y);
      g.addColorStop(0, "#111111");
      g.addColorStop(1, "#f5f5f5");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(s.x, s.y, r, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "rgba(0,0,0,0.25)";
      ctx.lineWidth = 1;
      ctx.stroke();
      label(ctx, "Transporte afuera", s.x, s.y - r - 6 * scale, 7 * scale);
    } else if (isPaletMarker(n.id)) {
      dot(4.2, V2_COLORS.morado);
    } else if (n.id.startsWith("RECO_")) {
      dot(4.8, V2_COLORS.naranja);
      label(ctx, markerLabel(n) ?? "R", s.x + 11 * scale, s.y - 7 * scale, 8.5 * scale);
    } else if (n.id.startsWith("INSUMO_")) {
      dot(4.8, V2_COLORS.amarillo);
      label(ctx, markerLabel(n) ?? "P", s.x + 11 * scale, s.y - 7 * scale, 8.5 * scale);
    } else if (n.id.startsWith("FUENTE_INSUMOS")) {
      dot(8, V2_COLORS.cafe);
      label(ctx, "Insumos", s.x, s.y + 15 * scale, 6.5 * scale);
    } else if (n.type === "carga") {
      dot(4.8, V2_COLORS.verde);
      label(ctx, "CARGADOR", s.x, s.y - 10 * scale, 6 * scale);
    } else if (n.type === "cruce") {
      // Los cruces se pintan una sola vez con su número abajo.
      continue;
    }
  }

  // Puntos azules: únicamente nodos cruce reales del layout.
  for (const point of bluePoints) {
    const screen = toScreen(point.x, point.y);
    ctx.fillStyle = V2_COLORS.azul;
    ctx.beginPath();
    ctx.arc(screen.x, screen.y, 2.6 * scale, 0, Math.PI * 2);
    ctx.fill();
    drawBluePointNumber(ctx, point, toScreen, scale);
  }
}
