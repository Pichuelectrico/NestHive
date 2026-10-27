// Contrato canónico — docs/API_CONTRATO.md

export type EstadoAMR =
  | "IDLE"
  | "MOVING_TO_PICKUP"
  | "LOADING"
  | "MOVING_TO_DELIVERY"
  | "UNLOADING"
  | "WAITING_OBSTACLE"
  | "REROUTING"
  | "CHARGING"
  | "ERROR";

export type TipoAMR = "pallet_lifter" | "towing_tug" | "unit_load";

export type TipoObstaculo = "OPERATOR" | "SPILL" | "BLOCK";

export interface AMRState {
  id: string;
  nombre: string;
  estado: EstadoAMR;
  x: number;
  y: number;
  angulo: number;
  bateria: number;
  tarea_asignada: string | null;
  path: string[];
  tipo: TipoAMR;
}

export interface LineaState {
  id: string;
  nombre: string;
  material: string;
  nivel_pct: number;
  minutos_restantes: number;
  is_packing?: boolean;
}

export interface ObstaculoState {
  id: string;
  tipo: TipoObstaculo;
  x: number;
  y: number;
  radius: number;
  edge: [string, string] | null;
}

export interface KPIsState {
  viajes_completados: number;
  viajes_vacios_evitados: number;
  paradas_evitadas: number;
  tiempo_medio_entrega_min: number;
  km_evitados: number;
  roi_km_pct: number;
  /** Tiempo medio (min) que un paquete espera en un OUT antes de ser entregado al muro */
  tiempo_medio_en_out_min: number;
}

/** Notice/banner del backend (ej. "⚡ PICO DE DEMANDA", derrames) */
export interface Notice {
  tipo: string;
  line_id?: string;
  mensaje?: string;
  sim_time?: number;
}

export interface SimulationSnapshot {
  sim_time: number;
  tick_id: number;
  amrs: AMRState[];
  lines: LineaState[];
  obstacles: ObstaculoState[];
  kpis: KPIsState;
  /** Banners opcionales: en LIVE vienen como objetos Notice; en modo offline como strings */
  notices?: (string | Notice)[];
  /** Paquetes terminados esperando la entrega exclusiva al muro (id nodo OUT → cantidad) */
  out_stock?: Record<string, number>;
}

export interface PlantInfo {
  id: string;
  nombre: string;
  layout_url?: string;
}

/** Arista seleccionada en el mapa (modo derrame interactivo) */
export interface SelectedEdge {
  from: string;
  to: string;
}

export type SpillMode = "none" | "block" | "unblock";

export type TipoTarea = "SUPPLY_REQUEST" | "PICKUP_PT" | "RECHARGE" | "RELOCATION" | "EXPEDITION" | "EXPORT";
export type EstadoTarea = "pendiente" | "asignada" | "en_curso" | "completada";

export interface Mission {
  id: string;
  tipo: TipoTarea;
  origen: string;
  destino: string;
  prioridad: number;
  estado: EstadoTarea;
  amr_asignado?: string | null;
}

export type TipoNodo =
  | "linea"
  | "empacadora"
  | "almacen"
  | "cruce"
  | "carga"
  | "buffer";

export interface LayoutNode {
  id: string;
  x: number;
  y: number;
  type: TipoNodo;
  label: string;
}

export interface LayoutEdge {
  from: string;
  to: string;
  length: number;
  max_speed: number;
  direction: string;
  blocked: boolean;
  /** Ruta exclusiva de entrega al muro (se pinta en rosa) */
  entrega?: boolean;
}

export interface LayoutPedestrian {
  id: string;
  name?: string;
  waypoints: string[];
  speed: number;
  radius: number;
}

/** Zona de fondo del mapa (rect en coords de layout). color "" = solo etiqueta; label "" = solo relleno. */
export interface LayoutZone {
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
  color: string;
}

/** Muro/pared física (no transpirable para AMRs ni humanos). Rect estrecho en coords de layout. */
export interface LayoutWall {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
  label?: string;
  color?: string;
}

/** Metadatos de línea de producción (opcional; consumido si backend lo envía). */
export interface LayoutLine {
  id: string;
  nombre?: string;
  color?: string;
  x?: number;
  y?: number;
  w?: number;
  h?: number;
  buffer_nodes?: string[];
}

export interface PlantLayout {
  canvas: { w: number; h: number; title: string };
  nodes: LayoutNode[];
  edges: LayoutEdge[];
  pedestrians: LayoutPedestrian[];
  /** Capas de fondo opcionales — impermeable si ausente/vacío */
  zones?: LayoutZone[];
  lines?: LayoutLine[];
  /** Muros/paredes físicas (no transpirables) — dibujados solid negro, impermeable si ausente/vacío */
  walls?: LayoutWall[];
  /** Zoom de vista por layout (1 = full-fit). <1 reduce el tamaño aparente del mapa (p.ej. 0.7 en plantas densas). */
  viewScale?: number;
}

/** Posición interpolada para render a 60fps */
export interface AMRRenderState extends AMRState {
  renderX: number;
  renderY: number;
}

export type ConnectionMode = "live" | "offline" | "connecting";
