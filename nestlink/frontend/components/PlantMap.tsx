"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AMR_STATE_COLORS } from "@/lib/amrColors";
import { getBatteryEmoji, resolveAmrCargoVisual } from "@/lib/amrCargo";
import { FLEET_PRESENTATION, tipoDeAmr } from "@/lib/config";
import { WIFI_APS_BY_PLANT } from "@/lib/config";
import { edgeKey, findEdgeAtScreenPoint } from "@/lib/edgeHit";
import { getAmrAnchor } from "@/lib/mapGeometry";
import { getLayoutBounds, type LayoutBounds } from "@/lib/layoutBounds";
import type {
  AMRRenderState,
  LayoutEdge,
  Mission,
  ObstaculoState,
  PlantLayout,
  SelectedEdge,
  SpillMode,
} from "@/lib/types";


/** Hex/rgb → rgba con alpha; si no parseable, null (usar globalAlpha). */
function colorWithAlpha(color: string, alpha: number): string | null {
  const c = color.trim();
  if (!c) return null;
  if (c.startsWith("#")) {
    let r = 0, g = 0, b = 0;
    if (c.length === 4) {
      r = parseInt(c[1] + c[1], 16);
      g = parseInt(c[2] + c[2], 16);
      b = parseInt(c[3] + c[3], 16);
    } else if (c.length >= 7) {
      r = parseInt(c.slice(1, 3), 16);
      g = parseInt(c.slice(3, 5), 16);
      b = parseInt(c.slice(5, 7), 16);
    } else {
      return null;
    }
    if ([r, g, b].some((v) => Number.isNaN(v))) return null;
    return `rgba(${r},${g},${b},${alpha})`;
  }
  const m = c.match(/^rgba?\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)/i);
  if (m) return `rgba(${m[1]},${m[2]},${m[3]},${alpha})`;
  return null;
}

/** Flecha de sentido u→v en el punto medio de la arista (capa estática). */
function drawDirectionArrow(
  ctx: CanvasRenderingContext2D,
  sa: { x: number; y: number },
  sb: { x: number; y: number },
  scale: number
) {
  const mx = (sa.x + sb.x) / 2;
  const my = (sa.y + sb.y) / 2;
  const angle = Math.atan2(sb.y - sa.y, sb.x - sa.x);
  const size = Math.max(4, 5.5 * scale);
  ctx.save();
  ctx.translate(mx, my);
  ctx.rotate(angle);
  ctx.fillStyle = "rgba(234, 211, 169, 0.55)";
  ctx.beginPath();
  ctx.moveTo(size, 0);
  ctx.lineTo(-size * 0.65, size * 0.55);
  ctx.lineTo(-size * 0.65, -size * 0.55);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

/** En mapas densos solo se etiquetan los nodos de interés (almacenes/líneas clave, empacadoras, cargadores). */
function isDenseLandmark(n: { id: string; type?: string }): boolean {
  if (getSemanticNodeColor(n.id)) return true;
  if (n.type === "empacadora" || n.type === "carga") return true;
  return /^(WH_MP_\d+|WH_PT_\d+|L\d+_OUT|E\d+_IN)$/.test(n.id);
}

/** Semántica New_map (planta espol_fusion): colores específicos por prefijo de nodo. */
function getSemanticNodeColor(id: string): string | null {
  if (id.startsWith("RECO_")) return "#f97316"; // naranja (puntos de recolección de pallets)
  if (id.startsWith("PALET_")) return "#8b5cf6"; // morado (zona de paletizaje)
  if (id.startsWith("TRANSPORTE")) return "#e4032e"; // rojo (hub de transporte externo)
  if (id.startsWith("INSUMO_")) return "#d29922"; // amarillo (colocación de insumos)
  if (id.startsWith("FUENTE_INSUMOS")) return "#92400e"; // café (fuente de insumos)
  return null;
}

/** Arista del dominio AMR (TRANSPORTE ↔ PALET_* o con domain: "AMR"). */
function isAmrEdge(e: LayoutEdge): boolean {
  if ((e as { domain?: string }).domain === "AMR") return true;
  return (
    (e.from.startsWith("TRANSPORTE") && e.to.startsWith("PALET_")) ||
    (e.to.startsWith("TRANSPORTE") && e.from.startsWith("PALET_"))
  );
}

interface PlantMapProps {
  layout: PlantLayout;
  layoutKey: number;
  amrs: AMRRenderState[];
  missions?: Mission[];
  obstacles: ObstaculoState[];
  spillMode: SpillMode;
  selectedEdge: SelectedEdge | null;
  onEdgeSelect: (edge: SelectedEdge | null) => void;
  /** Modo página única: fit real al viewport (sin viewScale) + pan/wheel zoom */
  interactive?: boolean;
  /** Planta activa — realistic → flota rojo Nestlé unificado */
  plantId?: string;
  /** Vista LiDAR: rutas como barrido + cono de avance */
  lidarMode?: boolean;
  /** Tiempo de simulación (s) — pulso LiDAR determinista */
  simTime?: number;
  /** Paquetes esperando en OUTs (id nodo → cantidad) → emoji 📦 en la ruta rosada */
  outStock?: Record<string, number>;
  /** Capa Wi-Fi: APs + halo (default OFF — pitch de red) */
  showWifiNetwork?: boolean;
}

export function PlantMap({
  layout,
  layoutKey,
  amrs,
  missions = [],
  obstacles,
  spillMode,
  selectedEdge,
  onEdgeSelect,
  interactive = false,
  plantId,
  lidarMode = false,
  simTime = 0,
  outStock,
  showWifiNetwork = false,
}: PlantMapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const transformRef = useRef({ scale: 1, offsetX: 0, offsetY: 0 });
  const boundsRef = useRef<LayoutBounds>(getLayoutBounds(layout));
  const fitScaleRef = useRef(1);
  const dragRef = useRef<{
    active: boolean;
    moved: boolean;
    lastX: number;
    lastY: number;
  }>({ active: false, moved: false, lastX: 0, lastY: 0 });
  const [hoveredEdge, setHoveredEdge] = useState<SelectedEdge | null>(null);
  const hoveredRef = useRef<SelectedEdge | null>(null);
  const [mapOpacity, setMapOpacity] = useState(1);
  const [panning, setPanning] = useState(false);

  const resize = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const panel = canvas.parentElement;
    if (!panel) return;

    canvas.width = panel.clientWidth;
    canvas.height = panel.clientHeight;

    const bounds = getLayoutBounds(layout);
    boundsRef.current = bounds;

    // Fullscreen: pad mínimo y SIN viewScale → llena el viewport (sin letterboxing)
    // Dashboard normal: conserva viewScale (Huge 0.7) + pad 40
    const pad = interactive ? 8 : 40;
    const fitScale = Math.min(
      (canvas.width - pad * 2) / Math.max(bounds.width, 1),
      (canvas.height - pad * 2) / Math.max(bounds.height, 1)
    );
    const viewScale =
      interactive
        ? 1
        : typeof layout.viewScale === "number" && layout.viewScale > 0
          ? layout.viewScale
          : 1;
    const scale = fitScale * viewScale;
    fitScaleRef.current = fitScale;

    transformRef.current = {
      scale,
      offsetX: (canvas.width - bounds.width * scale) / 2 - bounds.minX * scale,
      offsetY: (canvas.height - bounds.height * scale) / 2 - bounds.minY * scale,
    };
  }, [layout, interactive]);

  useEffect(() => {
    setMapOpacity(0.35);
    resize();
    const t = window.setTimeout(() => setMapOpacity(1), 120);
    return () => window.clearTimeout(t);
  }, [layout, layoutKey, resize]);

  const toScreen = (x: number, y: number) => {
    const { scale, offsetX, offsetY } = transformRef.current;
    // Medio píxel para trazos nítidos y centrados sobre la centerline
    const sx = offsetX + x * scale;
    const sy = offsetY + y * scale;
    return { x: Math.round(sx * 2) / 2, y: Math.round(sy * 2) / 2 };
  };

  const toLayout = (sx: number, sy: number) => {
    const { scale, offsetX, offsetY } = transformRef.current;
    return {
      x: (sx - offsetX) / scale,
      y: (sy - offsetY) / scale,
    };
  };

  const getBlockedEdges = useCallback(() => {
    const blocked = new Set<string>();
    obstacles.forEach((o) => {
      if (o.edge) blocked.add(edgeKey(o.edge[0], o.edge[1]));
    });
    layout.edges.forEach((e) => {
      if (e.blocked) blocked.add(edgeKey(e.from, e.to));
    });
    return blocked;
  }, [obstacles, layout.edges]);

  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { scale, offsetX, offsetY } = transformRef.current;
    const bounds = boundsRef.current;
    const blockedEdges = getBlockedEdges();
    const hover = hoveredRef.current;
    const sel = selectedEdge;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const bgX = offsetX + bounds.minX * scale;
    const bgY = offsetY + bounds.minY * scale;
    const bgW = bounds.width * scale;
    const bgH = bounds.height * scale;

    ctx.fillStyle = "#e8f4fc";
    ctx.fillRect(bgX, bgY, bgW, bgH);

    ctx.strokeStyle = "#c5dce8";
    ctx.lineWidth = 0.5;
    const gridStep = 40;
    for (
      let x = Math.floor(bounds.minX / gridStep) * gridStep;
      x <= bounds.maxX;
      x += gridStep
    ) {
      const s = toScreen(x, bounds.minY);
      ctx.beginPath();
      ctx.moveTo(s.x, bgY);
      ctx.lineTo(s.x, bgY + bgH);
      ctx.stroke();
    }
    for (
      let y = Math.floor(bounds.minY / gridStep) * gridStep;
      y <= bounds.maxY;
      y += gridStep
    ) {
      const s = toScreen(bounds.minX, y);
      ctx.beginPath();
      ctx.moveTo(bgX, s.y);
      ctx.lineTo(bgX + bgW, s.y);
      ctx.stroke();
    }

    // Lookup O(1) para mapas grandes (~500 nodos/aristas)
    const nodeById = new Map(layout.nodes.map((n) => [n.id, n]));
    // Mapa denso (p.ej. Huge: 520 nodos / 459 cruces / 57 zonas) → modo compacto:
    // cruces y slots de rack sin etiqueta, aristas finas, solo nodos clave rotulados.
    const dense = layout.nodes.length >= 150;
    // En mapas densos los sprites (AMRs/peatones) a tamaño completo tapan los pasillos:
    // se encogen con el mismo factor que nodos/aristas para que encajen con el mapa.
    const spriteK = dense ? 0.45 : 1;

    // Capas de fondo (zonas) — impermeable si ausente/vacío
    const zones = layout.zones;
    if (zones && zones.length > 0) {
      for (const zone of zones) {
        try {
          const tl = toScreen(zone.x, zone.y);
          const br = toScreen(zone.x + zone.w, zone.y + zone.h);
          const zx = Math.min(tl.x, br.x);
          const zy = Math.min(tl.y, br.y);
          const zw = Math.abs(br.x - tl.x);
          const zh = Math.abs(br.y - tl.y);
          const hasFill = Boolean(zone.color && zone.color.trim());
          const hasLabel = Boolean(zone.label && zone.label.trim());

          if (hasFill) {
            const fill = colorWithAlpha(zone.color, dense ? 0.12 : 0.18);
            if (fill) {
              ctx.fillStyle = fill;
              ctx.fillRect(zx, zy, zw, zh);
            } else {
              ctx.save();
              ctx.globalAlpha = 0.18;
              ctx.fillStyle = zone.color;
              ctx.fillRect(zx, zy, zw, zh);
              ctx.restore();
            }
            const stroke = colorWithAlpha(zone.color, dense ? 0.42 : 0.55) ?? zone.color;
            ctx.strokeStyle = stroke;
            ctx.lineWidth = dense ? 0.8 : 1;
            ctx.strokeRect(zx, zy, zw, zh);
          }

          if (hasLabel) {
            // En mapas densos solo etiquetar zonas suficientemente grandes (evita el letrero-masa)
            if (!dense || (zw >= 24 && zh >= 10)) {
              const fontPx = dense
                ? Math.max(9, Math.min(zw / 22, 28))
                : Math.max(10, Math.min(zw / 18, 48));
              ctx.save();
              ctx.fillStyle =
                colorWithAlpha(zone.color || "#1a3a4a", dense ? 0.45 : 0.35) ??
                "rgba(26,58,74,0.45)";
              ctx.font = `bold ${fontPx}px sans-serif`;
              ctx.textAlign = "left";
              ctx.textBaseline = "top";
              ctx.fillText(zone.label, zx + 6 * scale, zy + 4 * scale);
              ctx.restore();
            }
          }
        } catch {
          // Zona malformada — no tumbar el rAF
        }
      }
    }

    // Muros/paredes físicas (no transpirables) — dibujados como barras sólidas oscuras
    // justo debajo de aristas/nodos para que se vean como obstáculos reales del piso.
    const walls = layout.walls;
    if (walls && walls.length > 0) {
      for (const wl of walls) {
        try {
          const tl = toScreen(wl.x, wl.y);
          const br = toScreen(wl.x + wl.w, wl.y + wl.h);
          const wx = Math.min(tl.x, br.x);
          const wy = Math.min(tl.y, br.y);
          const ww = Math.max(1, Math.abs(br.x - tl.x));
          const wh = Math.max(1, Math.abs(br.y - tl.y));
          ctx.save();
          ctx.fillStyle = wl.color || "#1f2937";
          ctx.fillRect(wx, wy, ww, wh);
          // brillo superior para dar volumen a la pared
          ctx.strokeStyle = "rgba(255,255,255,0.25)";
          ctx.lineWidth = 1;
          ctx.strokeRect(wx + 0.5, wy + 0.5, ww - 1, wh - 1);
          if (wl.label && !dense) {
            const fontPx = Math.max(9, Math.min(ww / 4, 20));
            ctx.fillStyle = "#ffffff";
            ctx.font = `bold ${fontPx}px sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(wl.label, wx + ww / 2, wy + wh / 2);
          }
          ctx.restore();
        } catch {
          // Muro malformado — no tumbar el rAF
        }
      }
    }

    layout.edges.forEach((e: LayoutEdge) => {
      const na = nodeById.get(e.from);
      const nb = nodeById.get(e.to);
      if (!na || !nb) return;
      const sa = toScreen(na.x, na.y);
      const sb = toScreen(nb.x, nb.y);
      const key = edgeKey(e.from, e.to);
      const blocked = blockedEdges.has(key);
      const isHover = hover && edgeKey(hover.from, hover.to) === key;
      const isSel = sel && edgeKey(sel.from, sel.to) === key;

      ctx.beginPath();
      ctx.moveTo(sa.x, sa.y);
      ctx.lineTo(sb.x, sb.y);

      if (blocked) {
        ctx.strokeStyle = "#f85149";
        ctx.lineWidth = (dense ? 0.4 : 1) * (isHover || isSel ? 6 : 4) * scale;
        ctx.setLineDash([6, 4]);
      } else if (isSel) {
        ctx.strokeStyle = "#58a6ff";
        ctx.lineWidth = (dense ? 0.4 : 1) * 6 * scale;
        ctx.setLineDash([]);
      } else if (isHover) {
        ctx.strokeStyle = "#db6d28";
        ctx.lineWidth = (dense ? 0.4 : 1) * 5 * scale;
        ctx.setLineDash([]);
      } else if (e.entrega) {
        // Ruta rosada exclusiva de entrega al muro (OUT → pared externa)
        ctx.strokeStyle = "rgba(236,72,153,0.95)";
        ctx.lineWidth = (dense ? 0.6 : 1.4) * 4 * scale;
        ctx.setLineDash([]);
      } else if (isAmrEdge(e)) {
        // Aristas TRANSPORTE ↔ PALET_* (dominio AMR)
        ctx.strokeStyle = "#e4032e";
        ctx.lineWidth = (dense ? 0.4 : 1) * 3 * scale;
        ctx.setLineDash([]);
      } else {
        ctx.strokeStyle = dense ? "rgba(74,144,184,0.75)" : "#4a90b8";
        ctx.lineWidth = (dense ? 0.4 : 1) * 3 * scale;
        ctx.setLineDash([]);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Flecha de sentido en aristas unidireccionales (entre zonas y nodos)
      const dir = (e.direction || "bi").toLowerCase();
      if (dir !== "bi") {
        drawDirectionArrow(ctx, sa, sb, scale);
      }

      if (blocked) {
        const mx = (sa.x + sb.x) / 2;
        const my = (sa.y + sb.y) / 2;
        ctx.font = `${14 * scale}px sans-serif`;
        ctx.textAlign = "center";
        ctx.fillText("🚧", mx, my);
      }

      if (isSel && !blocked) {
        const mx = (sa.x + sb.x) / 2;
        const my = (sa.y + sb.y) / 2;
        ctx.fillStyle = "#58a6ff";
        ctx.font = `bold ${9 * scale}px sans-serif`;
        ctx.textAlign = "center";
        ctx.fillText(`${e.from}→${e.to}`, mx, my - 8 * scale);
      }
    });

    layout.nodes.forEach((n) => {
      try {
        const s = toScreen(n.x, n.y);
        const landmark = !dense || isDenseLandmark(n);
        const semanticColor = getSemanticNodeColor(n.id);

        if (n.type === "cruce") {
          // Cruce: punto; en mapas densos se omite la etiqueta para no saturar el plano
          const r = dense ? 1.6 * scale : 6 * scale;
          ctx.fillStyle = semanticColor ?? (dense ? "rgba(108,142,191,0.5)" : "#6c8ebf");
          ctx.beginPath();
          ctx.arc(s.x, s.y, r, 0, Math.PI * 2);
          ctx.fill();
          if (!dense) {
            ctx.fillStyle = semanticColor ? "#5b3918" : "#4a6a7a";
            ctx.font = `${7 * scale}px sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "alphabetic";
            ctx.fillText(n.id, s.x, s.y + 14 * scale);
          }
        } else if (n.type === "buffer") {
          const half = (dense ? 2.6 : 3.5) * scale;
          ctx.fillStyle = semanticColor ?? "#e8eef2";
          ctx.fillRect(s.x - half, s.y - half, half * 2, half * 2);
          ctx.strokeStyle = semanticColor ?? "#4a5560";
          ctx.lineWidth = 1;
          ctx.strokeRect(s.x - half, s.y - half, half * 2, half * 2);
          if ((!dense || semanticColor) && n.label) {
            ctx.fillStyle = semanticColor ? "#5b3918" : "#6a7a8a";
            ctx.font = `${6 * scale}px sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "alphabetic";
            ctx.fillText(n.label, s.x, s.y - half - 3 * scale);
          }
        } else if (!dense) {
          // === Vista normal (plantas pequeñas): glifo grande + etiqueta ===
          if (n.type === "linea") {
            ctx.fillStyle = semanticColor ?? "#2d6a4f";
            ctx.fillRect(s.x - 20 * scale, s.y - 12 * scale, 40 * scale, 24 * scale);
          } else if (n.type === "empacadora") {
            ctx.fillStyle = semanticColor ?? "#e85d04";
            ctx.fillRect(s.x - 20 * scale, s.y - 12 * scale, 40 * scale, 24 * scale);
          } else if (n.type === "almacen") {
            ctx.fillStyle = semanticColor ?? "#457b9d";
            ctx.fillRect(s.x - 22 * scale, s.y - 16 * scale, 44 * scale, 32 * scale);
            ctx.strokeStyle = semanticColor ? "rgba(255,255,255,0.45)" : "#a8dadc";
            ctx.lineWidth = 1;
            for (let i = 0; i < 3; i++) {
              ctx.beginPath();
              ctx.moveTo(s.x - 18 * scale, s.y - 12 * scale + i * 10 * scale);
              ctx.lineTo(s.x + 18 * scale, s.y - 12 * scale + i * 10 * scale);
              ctx.stroke();
            }
          } else if (n.type === "carga") {
            ctx.fillStyle = semanticColor ?? "#d29922";
            ctx.beginPath();
            ctx.arc(s.x, s.y, 12 * scale, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#fff";
            ctx.font = `${10 * scale}px sans-serif`;
            ctx.textAlign = "center";
            ctx.fillText("⚡", s.x, s.y + 4 * scale);
          } else {
            ctx.fillStyle = semanticColor ?? "#6c8ebf";
            ctx.beginPath();
            ctx.arc(s.x, s.y, 6 * scale, 0, Math.PI * 2);
            ctx.fill();
          }

          if (n.label) {
            ctx.fillStyle = semanticColor ? "#5b3918" : "#1a3a4a";
            ctx.font = `bold ${9 * scale}px sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "alphabetic";
            ctx.fillText(n.label, s.x, s.y - 18 * scale);
          }
        } else if (landmark) {
          // === Vista densa: solo nodos clave, glifos compactos y etiqueta con halo ===
          if (n.type === "linea") {
            ctx.fillStyle = semanticColor ?? "#2d6a4f";
            ctx.fillRect(s.x - 12 * scale, s.y - 8 * scale, 24 * scale, 16 * scale);
          } else if (n.type === "empacadora") {
            ctx.fillStyle = semanticColor ?? "#e85d04";
            ctx.fillRect(s.x - 10 * scale, s.y - 7 * scale, 20 * scale, 14 * scale);
          } else if (n.type === "almacen") {
            ctx.fillStyle = semanticColor ?? "#457b9d";
            ctx.fillRect(s.x - 13 * scale, s.y - 10 * scale, 26 * scale, 20 * scale);
            ctx.strokeStyle = semanticColor ? "rgba(255,255,255,0.45)" : "rgba(168,218,220,0.9)";
            ctx.lineWidth = 0.8;
            for (let i = 1; i < 3; i++) {
              ctx.beginPath();
              ctx.moveTo(s.x - 10 * scale, s.y - 6 * scale + i * 6 * scale);
              ctx.lineTo(s.x + 10 * scale, s.y - 6 * scale + i * 6 * scale);
              ctx.stroke();
            }
          } else if (n.type === "carga") {
            ctx.fillStyle = semanticColor ?? "#d29922";
            ctx.beginPath();
            ctx.arc(s.x, s.y, 8 * scale, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "#fff";
            ctx.font = `${7 * scale}px sans-serif`;
            ctx.textAlign = "center";
            ctx.fillText("⚡", s.x, s.y + 2.5 * scale);
          }

          if (n.label && n.type !== "carga") {
            const ly = s.y - (n.type === "almacen" ? 12 : 10) * scale;
            ctx.font = `bold ${7.5 * scale}px sans-serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "alphabetic";
            ctx.strokeStyle = "rgba(232,244,252,0.85)";
            ctx.lineWidth = 3;
            ctx.strokeText(n.label, s.x, ly);
            ctx.fillStyle = semanticColor ? "#5b3918" : "#1a3a4a";
            ctx.fillText(n.label, s.x, ly);
          }
        } else {
          // Infraestructura interna (slots de rack, puntos de línea): punto discreto sin texto
          ctx.fillStyle = n.type === "linea" ? "rgba(45,106,79,0.7)" : "rgba(69,123,157,0.6)";
          ctx.beginPath();
          ctx.arc(s.x, s.y, 2.6 * scale, 0, Math.PI * 2);
          ctx.fill();
        }
      } catch {
        // Nodo problemático — no tumbar el rAF
      }
    });

    // Ronda 15: emoji 📦 sobre cada OUT con paquete terminado esperando la entrega exclusiva al muro
    if (outStock) {
      layout.nodes.forEach((n) => {
        if (/^OUT/.test(n.id) && (outStock[n.id] || 0) > 0) {
          const s = toScreen(n.x, n.y);
          const fs = (dense ? 13 : 17) * scale;
          const ly = s.y - (dense ? 24 : 32) * scale;
          ctx.font = `${fs}px sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.strokeStyle = "rgba(255,255,255,0.9)";
          ctx.lineWidth = 3.5;
          ctx.strokeText("📦", s.x, ly);
          ctx.fillText("📦", s.x, ly);
        }
      });
    }

    // Capa Wi-Fi industrial (APs): solo si el toggle está ON — datos estáticos, sin lógica en el loop
    if (showWifiNetwork) {
      const aps =
        (plantId && WIFI_APS_BY_PLANT[plantId]) ||
        WIFI_APS_BY_PLANT.realistic ||
        [];
      for (const ap of aps) {
        try {
          const s = toScreen(ap.x, ap.y);
          const haloR = (dense ? 18 : 26) * scale;
          const dotR = (dense ? 2.5 : 3.5) * scale;
          // Halo de cobertura tenue
          const grad = ctx.createRadialGradient(s.x, s.y, dotR, s.x, s.y, haloR);
          grad.addColorStop(0, "rgba(228, 3, 46, 0.22)");
          grad.addColorStop(0.55, "rgba(228, 3, 46, 0.08)");
          grad.addColorStop(1, "rgba(228, 3, 46, 0)");
          ctx.fillStyle = grad;
          ctx.beginPath();
          ctx.arc(s.x, s.y, haloR, 0, Math.PI * 2);
          ctx.fill();
          // Punto AP
          ctx.fillStyle = "#E4032E";
          ctx.beginPath();
          ctx.arc(s.x, s.y, dotR, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = "rgba(255,255,255,0.85)";
          ctx.lineWidth = Math.max(1, 1.2 * scale);
          ctx.stroke();
        } catch {
          // AP malformado — no tumbar el rAF
        }
      }
    }

    obstacles
      .filter((o) => o.tipo === "OPERATOR")
      .forEach((p) => {
        const s = toScreen(p.x, p.y);
        const rad = p.radius * 4 * spriteK * scale;
        ctx.beginPath();
        ctx.arc(s.x, s.y, rad, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(219, 110, 40, 0.15)";
        ctx.fill();
        ctx.strokeStyle = "rgba(219, 110, 40, 0.5)";
        ctx.lineWidth = 1.5 * spriteK;
        ctx.stroke();
        ctx.fillStyle = "#db6d28";
        ctx.beginPath();
        ctx.arc(s.x, s.y, 8 * spriteK * scale, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.font = `${8 * spriteK * scale}px sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("🚶", s.x, s.y);
      });

    // Rutas y AMRs — join misión por id (tarea_asignada es string) + fallback path
    const missionById = new Map(missions.map((m) => [m.id, m]));

    // Leyenda LiDAR (pitch)
    if (lidarMode) {
      ctx.save();
      ctx.fillStyle = "rgba(36, 22, 9, 0.88)";
      ctx.fillRect(10, 10, 128, 22);
      ctx.fillStyle = "#7CFFB2";
      ctx.font = `bold ${11}px sans-serif`;
      ctx.textAlign = "left";
      ctx.textBaseline = "middle";
      ctx.fillText("LiDAR · SLAM run", 18, 21);
      ctx.restore();
    }

    amrs.forEach((amr) => {
      try {
        if (amr.path.length < 1) return;
        const { routeColor } = resolveAmrCargoVisual(amr, layout, missionById);
        const isMoving =
          amr.estado === "MOVING_TO_PICKUP" ||
          amr.estado === "MOVING_TO_DELIVERY";
        const isWaiting = amr.estado === "WAITING_OBSTACLE";
        const speed = isMoving ? 2 : isWaiting ? 0.5 : 0;
        // Pulso determinista con sim_time (LiDAR); Date.now solo en ruta clásica
        const dashOffset = lidarMode
          ? speed
            ? (simTime * speed * 18) % 20
            : 0
          : speed
            ? (Date.now() * speed * 0.02) % 20
            : 0;

        const anchor = getAmrAnchor(amr, layout);
        const start = toScreen(anchor.x, anchor.y);

        // Dirección de avance (siguiente nodo del path o angulo)
        let dirX = Math.cos((amr.angulo * Math.PI) / 180);
        let dirY = Math.sin((amr.angulo * Math.PI) / 180);
        const nextNode = nodeById.get(amr.path[0]);
        if (nextNode) {
          const ns = toScreen(nextNode.x, nextNode.y);
          const dx = ns.x - start.x;
          const dy = ns.y - start.y;
          const len = Math.hypot(dx, dy);
          if (len > 1e-3) {
            dirX = dx / len;
            dirY = dy / len;
          }
        }
        const heading = Math.atan2(dirY, dirX);

        if (lidarMode) {
          // Rastro path — glow cian LiDAR
          const pulse = 0.45 + 0.35 * Math.sin(simTime * 5 + amr.id.length);
          ctx.save();
          ctx.strokeStyle = `rgba(80, 255, 180, ${0.25 + pulse * 0.25})`;
          ctx.lineWidth = 5 * spriteK * scale;
          ctx.lineCap = "round";
          ctx.lineJoin = "round";
          ctx.shadowColor = "rgba(80, 255, 180, 0.55)";
          ctx.shadowBlur = 10 * scale;
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          amr.path.forEach((nid) => {
            const n = nodeById.get(nid);
            if (!n) return;
            const s2 = toScreen(n.x, n.y);
            ctx.lineTo(s2.x, s2.y);
          });
          ctx.stroke();

          // Barrido punteado sobre el path
          ctx.shadowBlur = 0;
          ctx.strokeStyle = `rgba(180, 255, 220, ${0.55 + pulse * 0.3})`;
          ctx.lineWidth = 1.6 * spriteK * scale;
          ctx.setLineDash([5, 7]);
          ctx.lineDashOffset = -dashOffset;
          ctx.stroke();
          ctx.setLineDash([]);

          // Cono / spotlight en dirección de avance
          const reach = (isMoving ? 38 : isWaiting ? 22 : 16) * spriteK * scale;
          const spread = (Math.PI / 5) * (0.85 + 0.15 * pulse);
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          ctx.arc(start.x, start.y, reach, heading - spread, heading + spread);
          ctx.closePath();
          const grad = ctx.createRadialGradient(
            start.x,
            start.y,
            2,
            start.x,
            start.y,
            reach
          );
          grad.addColorStop(0, `rgba(120, 255, 200, ${0.35 + pulse * 0.2})`);
          grad.addColorStop(0.55, `rgba(80, 255, 180, ${0.12 + pulse * 0.08})`);
          grad.addColorStop(1, "rgba(80, 255, 180, 0)");
          ctx.fillStyle = grad;
          ctx.fill();

          // Rayo central de barrido
          ctx.strokeStyle = `rgba(220, 255, 240, ${0.5 + pulse * 0.35})`;
          ctx.lineWidth = 1.2 * spriteK * scale;
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          ctx.lineTo(
            start.x + Math.cos(heading) * reach,
            start.y + Math.sin(heading) * reach
          );
          ctx.stroke();
          ctx.restore();
        } else {
          ctx.save();
          ctx.strokeStyle = routeColor;
          ctx.lineWidth = 2 * spriteK * scale;
          ctx.globalAlpha = 0.55;
          ctx.setLineDash([8, 6]);
          ctx.lineDashOffset = -dashOffset;
          ctx.beginPath();
          ctx.moveTo(start.x, start.y);
          amr.path.forEach((nid) => {
            const n = nodeById.get(nid);
            if (!n) return;
            const s2 = toScreen(n.x, n.y);
            ctx.lineTo(s2.x, s2.y);
          });
          ctx.stroke();
          ctx.restore();
        }
      } catch {
        // No tumbar el bucle de dibujo por un AMR con datos incompletos
      }
    });

    amrs.forEach((amr, i) => {
      try {
        const anchor = getAmrAnchor(amr, layout);
        const s = toScreen(anchor.x, anchor.y);
        const ring = AMR_STATE_COLORS[amr.estado] ?? "#8b949e";
        const { cargoEmoji } = resolveAmrCargoVisual(amr, layout, missionById);

        ctx.beginPath();
        ctx.arc(s.x, s.y, 16 * spriteK * scale, 0, Math.PI * 2);
        ctx.strokeStyle = ring;
        ctx.lineWidth = 3 * spriteK * scale;
        ctx.stroke();

        const fleetType = tipoDeAmr(amr.id);
        const typeColor = fleetType === "AMR" ? FLEET_PRESENTATION.AMR_COLOR : FLEET_PRESENTATION.AGV_COLOR;
        ctx.fillStyle = typeColor;
        const w = 20 * spriteK * scale;
        const h = 16 * spriteK * scale;
        ctx.beginPath();
        ctx.roundRect(s.x - w / 2, s.y - h / 2, w, h, 4 * spriteK * scale);
        ctx.fill();

        ctx.fillStyle = "#5B3918";
        ctx.font = `bold ${8 * spriteK * scale}px sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "alphabetic";
        const amrLabel = FLEET_PRESENTATION.NAME_OVERRIDES[amr.id] ?? amr.nombre;
        ctx.fillText(amrLabel, s.x, s.y - 22 * spriteK * scale);
        ctx.font = `${Math.max(8, 9 * spriteK * scale)}px Arial, sans-serif`;
        ctx.fillStyle = typeColor;
        ctx.fillText(fleetType, s.x + ctx.measureText(amrLabel).width / 2 + 5, s.y - 22 * spriteK * scale);

        ctx.font = `${11 * spriteK * scale}px sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(`${cargoEmoji} ${getBatteryEmoji(amr)}`, s.x, s.y - 30 * spriteK * scale);

        const bw = 24 * spriteK * scale;
        ctx.fillStyle = "#5B3918";
        ctx.fillRect(s.x - bw / 2, s.y + 12 * spriteK * scale, bw, 4 * spriteK * scale);
        ctx.fillStyle = amr.bateria > 30 ? "#3fb950" : "#f85149";
        ctx.fillRect(
          s.x - bw / 2,
          s.y + 12 * spriteK * scale,
          bw * (amr.bateria / 100),
          4 * spriteK * scale
        );
      } catch {
        // Saltar AMR problemático; el resto sigue visible
      }
    });
  }, [layout, amrs, missions, obstacles, spillMode, selectedEdge, getBlockedEdges, plantId, lidarMode, simTime, outStock, showWifiNetwork]);

  useEffect(() => {
    resize();
    window.addEventListener("resize", resize);
    return () => window.removeEventListener("resize", resize);
  }, [resize]);

  useEffect(() => {
    let id = 0;
    const loop = () => {
      draw();
      id = requestAnimationFrame(loop);
    };
    id = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(id);
  }, [draw]);

  const clientToCanvas = (clientX: number, clientY: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return { sx: 0, sy: 0 };
    const rect = canvas.getBoundingClientRect();
    const scaleX = rect.width > 0 ? canvas.width / rect.width : 1;
    const scaleY = rect.height > 0 ? canvas.height / rect.height : 1;
    return {
      sx: (clientX - rect.left) * scaleX,
      sy: (clientY - rect.top) * scaleY,
    };
  };

  const handlePointer = (
    clientX: number,
    clientY: number,
    isClick: boolean
  ) => {
    if (spillMode === "none") return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const { sx, sy } = clientToCanvas(clientX, clientY);
    const hit = findEdgeAtScreenPoint(layout, sx, sy, toScreen, 18);

    if (!hit) {
      if (isClick) onEdgeSelect(null);
      hoveredRef.current = null;
      setHoveredEdge(null);
      return;
    }

    const blockedEdges = getBlockedEdges();
    const key = edgeKey(hit.from, hit.to);
    const isBlocked = blockedEdges.has(key);

    if (spillMode === "block" && isBlocked) {
      if (isClick) onEdgeSelect(null);
      hoveredRef.current = null;
      setHoveredEdge(null);
      return;
    }
    if (spillMode === "unblock" && !isBlocked) {
      if (isClick) onEdgeSelect(null);
      hoveredRef.current = null;
      setHoveredEdge(null);
      return;
    }

    const edge = { from: hit.from, to: hit.to };
    hoveredRef.current = edge;
    setHoveredEdge(edge);
    if (isClick) onEdgeSelect(edge);
  };

  // Wheel zoom (solo interactive) — non-passive para preventDefault
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !interactive) return;

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const { sx, sy } = clientToCanvas(e.clientX, e.clientY);
      const t = transformRef.current;
      const factor = e.deltaY < 0 ? 1.12 : 1 / 1.12;
      const base = fitScaleRef.current;
      const minS = base * 0.4;
      const maxS = base * 12;
      const newScale = Math.min(maxS, Math.max(minS, t.scale * factor));
      if (Math.abs(newScale - t.scale) < 1e-9) return;
      const lx = (sx - t.offsetX) / t.scale;
      const ly = (sy - t.offsetY) / t.scale;
      t.scale = newScale;
      t.offsetX = sx - lx * newScale;
      t.offsetY = sy - ly * newScale;
    };

    canvas.addEventListener("wheel", onWheel, { passive: false });
    return () => canvas.removeEventListener("wheel", onWheel);
  }, [interactive, layoutKey]);

  const onMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!interactive || e.button !== 0) return;
    // En modo derrame el click selecciona arista; pan solo si spillMode === none
    if (spillMode !== "none") return;
    dragRef.current = {
      active: true,
      moved: false,
      lastX: e.clientX,
      lastY: e.clientY,
    };
    setPanning(true);
  };

  const onMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const drag = dragRef.current;
    if (interactive && drag.active) {
      const dx = e.clientX - drag.lastX;
      const dy = e.clientY - drag.lastY;
      if (!drag.moved && Math.hypot(dx, dy) > 3) drag.moved = true;
      if (drag.moved) {
        const canvas = canvasRef.current;
        if (canvas) {
          const rect = canvas.getBoundingClientRect();
          const scaleX = rect.width > 0 ? canvas.width / rect.width : 1;
          const scaleY = rect.height > 0 ? canvas.height / rect.height : 1;
          transformRef.current.offsetX += dx * scaleX;
          transformRef.current.offsetY += dy * scaleY;
        }
        drag.lastX = e.clientX;
        drag.lastY = e.clientY;
      }
      return;
    }

    if (spillMode === "none") {
      hoveredRef.current = null;
      setHoveredEdge(null);
      return;
    }
    handlePointer(e.clientX, e.clientY, false);
  };

  const endDrag = () => {
    if (dragRef.current.active) {
      dragRef.current.active = false;
      setPanning(false);
    }
  };

  const onMouseUp = () => {
    endDrag();
  };

  const onClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    // Ignorar click si fue un pan
    if (dragRef.current.moved) {
      dragRef.current.moved = false;
      return;
    }
    if (spillMode === "none") return;
    handlePointer(e.clientX, e.clientY, true);
  };

  const onMouseLeave = () => {
    endDrag();
    hoveredRef.current = null;
    setHoveredEdge(null);
  };

  const cursor = panning
    ? "grabbing"
    : spillMode !== "none"
      ? hoveredEdge
        ? "pointer"
        : "crosshair"
      : interactive
        ? "grab"
        : "default";

  return (
    <canvas
      ref={canvasRef}
      className="block w-full h-full transition-opacity duration-300 ease-out"
      style={{ cursor, opacity: mapOpacity, touchAction: interactive ? "none" : undefined }}
      aria-label="Mapa 2D de planta NestHive"
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onClick={onClick}
      onMouseLeave={onMouseLeave}
    />
  );
}
