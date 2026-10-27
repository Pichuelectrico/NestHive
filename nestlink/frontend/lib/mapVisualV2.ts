/**
 * Renderer visual v2 de espol_fusion (estilo New_map.png).
 *
 * La GEOMETRÍA sale del grafo de simulación (nodos/aristas de espol_fusion.json): los
 * corredores son las aristas reales, así los agentes siempre circulan sobre lo dibujado.
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

const WALL_PAD = 22;
const CORRIDOR_W = 9;

function isTransportEdge(e: LayoutEdge): boolean {
  if ((e as { domain?: string }).domain === "AMR") return true;
  return e.from.startsWith("TRANSPORTE") || e.to.startsWith("TRANSPORTE");
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
    { nodes: layout.nodes.filter((n) => n.id.startsWith("PALET_")), pad: 8, color: V2_COLORS.morado, title: "Paletizaje" },
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
  const palet = layout.nodes.filter((n) => n.id.startsWith("PALET_"));
  const rows: LayoutNode[][] = [];
  for (const n of [...palet].sort((a, b) => a.y - b.y)) {
    const row = rows.find((r) => Math.abs(r[0].y - n.y) < 8);
    if (row) row.push(n);
    else rows.push([n]);
  }
  const target = rows[1] ?? rows[0];
  if (target) {
    const right = target.reduce((a, b) => (b.x > a.x ? b : a));
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
  const b = bbox(layout.nodes);

  // Fondo crema de planta (sin cuadrícula, como el plano del usuario)
  const tl = toScreen(b.minX - WALL_PAD, b.minY - WALL_PAD);
  const br = toScreen(b.maxX + WALL_PAD, b.maxY + WALL_PAD);
  ctx.fillStyle = V2_COLORS.fondo;
  ctx.fillRect(tl.x, tl.y, br.x - tl.x, br.y - tl.y);

  // Muro perimetral punteado gris (estilo New_map.png)
  ctx.save();
  ctx.strokeStyle = V2_COLORS.muro;
  ctx.lineWidth = Math.max(1.5, 1.6 * scale);
  ctx.setLineDash([3 * scale, 3 * scale]);
  ctx.strokeRect(tl.x, tl.y, br.x - tl.x, br.y - tl.y);
  ctx.restore();

  // Zonas semánticas alrededor de los nodos reales
  for (const z of semanticZones(layout)) zoneAround(ctx, z.nodes, z.pad, z.color, toScreen, scale);

  // Corredores: banda ancha bajo cada arista de circulación (no las del dominio AMR)
  const corridorEdges = layout.edges.filter((e) => !isTransportEdge(e));
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

  // Flechas rojas del dominio AMR: paletizaje ↔ transporte
  ctx.save();
  ctx.strokeStyle = V2_COLORS.rojo;
  ctx.globalAlpha = 0.5;
  ctx.lineWidth = Math.max(1, 1.1 * scale);
  for (const e of layout.edges.filter(isTransportEdge)) {
    const a = nodeById.get(e.from);
    const c = nodeById.get(e.to);
    if (!a || !c) continue;
    const sa = toScreen(a.x, a.y);
    const sc = toScreen(c.x, c.y);
    ctx.beginPath();
    ctx.moveTo(sa.x, sa.y);
    ctx.lineTo(sc.x, sc.y);
    ctx.stroke();
    const ang = Math.atan2(sc.y - sa.y, sc.x - sa.x);
    const back = 7 * scale;
    arrowHead(ctx, { x: sc.x - Math.cos(ang) * back, y: sc.y - Math.sin(ang) * back }, ang, 3.4 * scale, V2_COLORS.rojo);
    arrowHead(ctx, { x: sa.x + Math.cos(ang) * back, y: sa.y + Math.sin(ang) * back }, ang + Math.PI, 3.4 * scale, V2_COLORS.rojo);
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
    } else if (n.id.startsWith("PALET_")) {
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
      dot(2.6, V2_COLORS.azul);
    } else {
      // Almacenes, líneas, empacadoras y buffers: chip sobrio con su nombre real
      const w = 30 * scale;
      const h = 12 * scale;
      ctx.save();
      ctx.fillStyle = "#fffdf7";
      ctx.strokeStyle = n.type === "almacen" ? V2_COLORS.cafe : V2_COLORS.texto;
      ctx.lineWidth = 1;
      ctx.beginPath();
      roundedRect(ctx, s.x - w / 2, s.y - h / 2, w, h, 3 * scale);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
      label(ctx, n.label || n.id, s.x, s.y, 5.2 * scale);
    }
  }
}
