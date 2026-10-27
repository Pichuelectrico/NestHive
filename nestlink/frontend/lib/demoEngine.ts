/**
 * Motor demo offline — seed fijo 42, mismo contrato SimulationSnapshot.
 * Activa si el backend no responde en 3s.
 */
import type {
  AMRState,
  Mission,
  PlantLayout,
  SimulationSnapshot,
  TipoObstaculo,
} from "./types";

function mulberry32(seed: number) {
  return function () {
    seed |= 0;
    seed = seed + 0x6d2b79f5 | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = t + Math.imul(t ^ (t >>> 7), 61 | t) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function edgeKey(a: string, b: string) {
  return a < b ? `${a}-${b}` : `${b}-${a}`;
}

interface AmrSim {
  def: AMRState;
  routeKey: string;
  path: string[];
  segIdx: number;
  t: number;
  speed: number;
  dir: 1 | -1; // ping-pong en rutas: evita teletransporte al cerrar el lazo
  waitTicks: number; // paciencia anti-atasco ante peatones (≈1.6 s)
}

export class DemoEngine {
  private rng = mulberry32(42);
  private tickId = 0;
  private simTime = 14 * 60 + 23;
  private layout: PlantLayout;
  private blocked = new Set<string>();
  private pendingNotices: string[] = [];
  private missions: Mission[];
  private kpis = {
    viajes_completados: 12,
    viajes_vacios_evitados: 7,
    paradas_evitadas: 3,
    tiempo_medio_entrega_min: 4.2,
    km_evitados: 4.8,
    roi_km_pct: 22,
    tiempo_medio_en_out_min: 1.8,
  };

  private routes: Record<string, string[]> = {};
  private altRoutes: Record<string, string[]> = {};
  private chargingTarget = new Map<string, string>();
  private amrSims: AmrSim[] = [];
  private pedState: Array<{
    id: string;
    waypoints: string[];
    wpIdx: number;
    t: number;
    speed: number;
    radius: number;
    x: number;
    y: number;
  }> = [];

  private lineLevels: Record<
    string,
    { nombre: string; material: string; nivel_pct: number; minutos_restantes: number }
  > = {};

  constructor(layout: PlantLayout) {
    this.layout = layout;
    this.initRoutes();
    this.initAmrs();
    this.initPedestrians();
    this.initLines();
    this.missions = this.seedMissions();
  }

  private node(id: string) {
    const n = this.layout.nodes.find((x) => x.id === id);
    if (!n) throw new Error(`nodo ${id}`);
    return n;
  }

  private initRoutes() {
    // Rutas CALCULADAS con el grafo real del layout (nodos + aristas, BFS), en lugar de
    // nodos hardcodeados del mapa clásico. Los extremos semánticos existen en quito Y realistic,
    // así el modo offline funciona en cualquier planta. Si falta algún extremo o no hay
    // conexión, findPath devuelve [a, b] y la simulación sigue viva.
    const prim: Array<[string, string]> = [
      ["L1_OUT", "L2_OUT"], // amr1: bodega PT → línea 2
      ["E1_IN", "WH_MP_1"], // amr2: insumos → Savoy
      ["L2_OUT", "E1_IN"], // amr3: PT línea 2 → insumos
      ["E2_IN", "CHARGER_1"], // amr4: reserva + ruta al cargador
    ];
    const alt: Array<[string, string]> = [
      ["L1_OUT", "WH_PT_2"],
      ["E1_IN", "WH_PT_1"],
      ["L2_OUT", "WH_PT_2"],
      ["E2_IN", "CHARGER_2"],
    ];
    const keys: Array<keyof typeof this.routes> = ["amr1", "amr2", "amr3", "amr4"];
    const rr: typeof this.routes = {};
    const ar: typeof this.routes = {};
    keys.forEach((k, i) => {
      rr[k] = this.findPath(prim[i][0], prim[i][1]);
      ar[k] = this.findPath(alt[i][0], alt[i][1]);
    });
    this.routes = rr;
    this.altRoutes = ar;
  }

  private adjacency?: Map<string, string[]>;

  private buildAdjacency(): Map<string, string[]> {
    const adj = new Map<string, string[]>();
    for (const e of this.layout.edges) {
      const a = e.from;
      const b = e.to;
      if (typeof a !== "string" || typeof b !== "string") continue;
      if (!adj.has(a)) adj.set(a, []);
      if (!adj.has(b)) adj.set(b, []);
      adj.get(a)!.push(b);
      adj.get(b)!.push(a);
    }
    return adj;
  }

  /** BFS por las aristas del layout: ruta válida entre dos nodos (o [a,b] si no hay conexión). */
  private findPath(a: string, b: string): string[] {
    if (a === b) return [a];
    this.adjacency = this.adjacency ?? this.buildAdjacency();
    if (!this.adjacency.has(a) || !this.adjacency.has(b)) return [a, b];
    const prev = new Map<string, string | null>();
    const seen = new Set<string>([a]);
    const queue = [a];
    prev.set(a, null);
    while (queue.length) {
      const cur = queue.shift()!;
      if (cur === b) {
        const path: string[] = [];
        let n: string | null = b;
        while (n) {
          path.unshift(n);
          n = prev.get(n) ?? null;
        }
        return path;
      }
      for (const nb of this.adjacency.get(cur)!) {
        if (!seen.has(nb)) {
          seen.add(nb);
          prev.set(nb, cur);
          queue.push(nb);
        }
      }
    }
    return [a, b];
  }

  private initAmrs() {
    const defs: Omit<AMRState, "x" | "y" | "angulo">[] = [
      {
        id: "AMR_01",
        nombre: "Nescafé Shuttle",
        estado: "MOVING_TO_DELIVERY",
        bateria: 82,
        tarea_asignada: "TSK_06",
        path: [],
        tipo: "pallet_lifter",
      },
      {
        id: "AMR_02",
        nombre: "Savoy Express",
        estado: "MOVING_TO_DELIVERY",
        bateria: 65,
        tarea_asignada: "TSK_02",
        path: [],
        tipo: "unit_load",
      },
      {
        id: "AMR_03",
        nombre: "MAGGI Runner",
        estado: "MOVING_TO_PICKUP",
        bateria: 91,
        tarea_asignada: "TSK_03",
        path: [],
        tipo: "towing_tug",
      },
      {
        id: "AMR_04",
        nombre: "Lechera Hauler",
        estado: "MOVING_TO_DELIVERY",
        bateria: 45,
        tarea_asignada: "TSK_04",
        path: [],
        tipo: "pallet_lifter",
      },
    ];

    this.amrSims = defs.map((d, i) => {
      const routeKey = `amr${i + 1}`;
      const path = this.routes[routeKey];
      const start = this.node(path[0]);
      return {
        def: { ...d, x: start.x, y: start.y, angulo: 0, path: path.slice(1) },
        routeKey,
        path,
        segIdx: 0,
        t: 0,
        speed: 28 + this.rng() * 12, // px/s reales de navegación (pacing visual del modo offline)
        dir: 1,
        waitTicks: 0,
      };
    });
  }

  private initPedestrians() {
    this.pedState = this.layout.pedestrians.map((p) => {
      const start = this.node(p.waypoints[0]);
      return {
        id: p.id,
        waypoints: p.waypoints,
        wpIdx: 0,
        t: 0,
        speed: (p.speed / 10) * 9, // px/s reales (peatones ~8-9, visibles y que dejan pasar a los AMR)
        radius: p.radius,
        x: start.x,
        y: start.y,
      };
    });
  }

  private initLines() {
    const defaults = [
      { id: "E1_IN", nombre: "E1 Savoy (Insumos)", material: "Film Laminado 120mm" },
      { id: "E2_IN", nombre: "E2 La Lechera (Insumos)", material: "Corrugado 12oz" },
      { id: "L2_OUT", nombre: "L2 Maggi (PT)", material: "Bobina Pouch" },
      { id: "L1_OUT", nombre: "L1 Nescafé (PT)", material: "Pallet PT 48x40" },
    ];
    defaults.forEach((d) => {
      this.lineLevels[d.id] = {
        ...d,
        nivel_pct: 30 + this.rng() * 50,
        minutos_restantes: 5 + this.rng() * 30,
      };
    });
  }

  private seedMissions(): Mission[] {
    return [
      {
        id: "TSK_01",
        tipo: "SUPPLY_REQUEST",
        origen: "WH_MP_1",
        destino: "E1_IN",
        prioridad: 10,
        estado: "pendiente",
        amr_asignado: null,
      },
      {
        id: "TSK_02",
        tipo: "SUPPLY_REQUEST",
        origen: "WH_MP_1",
        destino: "E1_IN",
        prioridad: 8,
        estado: "en_curso",
        amr_asignado: "Savoy Express",
      },
      {
        id: "TSK_03",
        tipo: "PICKUP_PT",
        origen: "L2_OUT",
        destino: "WH_PT_2",
        prioridad: 5,
        estado: "asignada",
        amr_asignado: "MAGGI Runner",
      },
      {
        id: "TSK_04",
        tipo: "PICKUP_PT",
        origen: "E2_IN",
        destino: "WH_MP_2",
        prioridad: 3,
        estado: "en_curso",
        amr_asignado: "Lechera Hauler",
      },
      {
        id: "TSK_05",
        tipo: "SUPPLY_REQUEST",
        origen: "WH_MP_2",
        destino: "E2_IN",
        prioridad: 8,
        estado: "pendiente",
        amr_asignado: null,
      },
      {
        id: "TSK_06",
        tipo: "PICKUP_PT",
        origen: "L1_OUT",
        destino: "WH_PT_1",
        prioridad: 3,
        estado: "completada",
        amr_asignado: "Nescafé Shuttle",
      },
    ];
  }

  getMissions(): Mission[] {
    return [...this.missions].sort((a, b) => b.prioridad - a.prioridad);
  }

  toggleBlock(from: string, to: string): boolean {
    const key = edgeKey(from, to);
    if (this.blocked.has(key)) {
      this.blocked.delete(key);
      this.pendingNotices.push(`🔓 Pasillo despejado: ${from}–${to}`);
      return false;
    }
    this.blocked.add(key);
    this.pendingNotices.push(`🚧 Derrame en ${from}–${to}`);
    this.amrSims.forEach((a) => {
      a.def.estado = "REROUTING";
      a.t = 0;
      a.segIdx = 0;
    });
    return true;
  }

  injectPeak(lineId: string) {
    this.pendingNotices.push("⚡ PICO DE DEMANDA");
    const line = this.lineLevels[lineId];
    if (line) {
      line.nivel_pct = Math.max(5, line.nivel_pct - 30);
      if (line.nivel_pct < 25) {
        this.missions.unshift({
          id: `TSK_${Date.now()}`,
          tipo: "SUPPLY_REQUEST",
          origen: "WH_MP_1",
          destino: lineId,
          prioridad: 10,
          estado: "pendiente",
          amr_asignado: null,
        });
        this.kpis.paradas_evitadas += 1;
      }
    }
  }

  simulateRefill(lineId?: string | null, targetPct = 80): string[] {
    const empacadoras = Object.keys(this.lineLevels).filter((id) =>
      id.startsWith("E") && id.endsWith("_IN")
    );
    const targets = lineId ? [lineId] : empacadoras;
    const scheduled: string[] = [];

    targets.forEach((id) => {
      const line = this.lineLevels[id];
      if (!line) return;
      line.nivel_pct = Math.max(line.nivel_pct, targetPct);
      line.minutos_restantes = Math.max(line.minutos_restantes, 20);
      scheduled.push(id);
      this.missions.unshift({
        id: `TSK_refill_${id}_${this.tickId}`,
        tipo: "SUPPLY_REQUEST",
        origen: "WH_MP_1",
        destino: id,
        prioridad: 8,
        estado: "pendiente",
        amr_asignado: null,
      });
    });

    if (scheduled.length) {
      this.pendingNotices.push(
        `⌛ Metas >${targetPct}% fijadas: ${scheduled.join(", ")}`
      );
    }
    return scheduled;
  }

  simulateLowBattery(amrId: string) {
    const sim = this.amrSims.find((s) => s.def.id === amrId);
    if (!sim) return;

    const chargers = this.layout.nodes.filter((n) => n.type === "carga");
    if (chargers.length === 0) {
      chargers.push({ id: "CHARGER_1", x: 400, y: 40, type: "carga", label: "Cargador 1" });
    }

    // Calcular ocupación por otros AMRs (un solo conteo por AMR en recarga)
    const occupancyMap: Record<string, number> = {};
    for (const ch of chargers) {
      occupancyMap[ch.id] = 0;
    }
    for (const other of this.amrSims) {
      if (other.def.id === amrId) continue;
      const tgt = this.chargingTarget.get(other.def.id);
      if (tgt && occupancyMap[tgt] !== undefined) {
        occupancyMap[tgt]++;
      }
    }

    // Ordenar: 1º menor ocupación, 2º menor distancia euclidiana a la posición actual
    const sortedChargers = [...chargers].sort((a, b) => {
      const occDiff = (occupancyMap[a.id] ?? 0) - (occupancyMap[b.id] ?? 0);
      if (occDiff !== 0) return occDiff;
      const distA = Math.hypot(sim.def.x - a.x, sim.def.y - a.y);
      const distB = Math.hypot(sim.def.x - b.x, sim.def.y - b.y);
      return distA - distB;
    });

    const charger = sortedChargers[0]?.id ?? "CHARGER_1";
    const missionId = `TSK_recharge_${amrId}_${this.tickId}`;
    sim.def.bateria = 15;
    sim.def.estado = "CHARGING";
    sim.def.tarea_asignada = missionId;
    this.chargingTarget.set(amrId, charger);
    sim.path = this.findRouteToNode(charger, sim);
    sim.segIdx = 0;
    sim.t = 0;
    this.missions.unshift({
      id: missionId,
      tipo: "RECHARGE",
      origen: sim.path.length ? sim.path[0] : charger,
      destino: charger,
      prioridad: 8,
      estado: "en_curso",
      amr_asignado: amrId,
    });
    this.pendingNotices.push(
      `🔋 ${sim.def.nombre} batería 15% → yendo a ${charger}`
    );
  }

  private findRouteToNode(targetId: string, sim?: AmrSim): string[] {
    const fromNode = sim
      ? this.nearestNodeId(sim.def.x, sim.def.y)
      : null;

    const buildFromRoute = (route: string[]): string[] => {
      if (!route.includes(targetId)) return [];
      const idx = route.indexOf(targetId);
      if (fromNode && route.includes(fromNode)) {
        const start = route.indexOf(fromNode);
        if (start <= idx) return route.slice(start, idx + 1);
      }
      return route.slice(0, idx + 1);
    };

    for (const route of Object.values(this.routes)) {
      const segment = buildFromRoute(route);
      if (segment.length) return segment;
    }
    for (const route of Object.values(this.altRoutes)) {
      const segment = buildFromRoute(route);
      if (segment.length) return segment;
    }

    // Fallback seguro (cualquier planta): enlace directo nodo actual → objetivo
    const targetNode = this.layout.nodes.find((n) => n.id === targetId);
    if (fromNode && targetNode) return [fromNode, targetId];
    return [targetId];
  }

  private nearestNodeId(x: number, y: number): string | null {
    let best: string | null = null;
    let bestD = Infinity;
    for (const n of this.layout.nodes) {
      const d = Math.hypot(n.x - x, n.y - y);
      if (d < bestD) {
        bestD = d;
        best = n.id;
      }
    }
    return best;
  }

  private routeFor(sim: AmrSim): string[] {
    if (sim.def.estado === "CHARGING" && this.chargingTarget.has(sim.def.id)) {
      const target = this.chargingTarget.get(sim.def.id)!;
      return this.findRouteToNode(target, sim);
    }
    return this.activeRoute(sim);
  }

  private activeRoute(sim: AmrSim): string[] {
    const primary = this.routes[sim.routeKey];
    // Si algún tramo del recorrido primario está bloqueado → alternativo (funciona en
    // cualquier planta y para cualquier arista bloqueada, no solo el par hardcodeado del mapa clásico).
    if (primary) {
      for (let i = 0; i < primary.length - 1; i++) {
        if (this.isBlocked(primary[i], primary[i + 1])) {
          return this.altRoutes[sim.routeKey] ?? primary;
        }
      }
    }
    return primary ?? sim.path;
  }

  private isBlocked(from: string, to: string) {
    return this.blocked.has(edgeKey(from, to));
  }

  private dist(ax: number, ay: number, bx: number, by: number) {
    return Math.hypot(bx - ax, by - ay);
  }

  private advanceAmr(sim: AmrSim) {
    const route = this.routeFor(sim);
    if (sim.path !== route) {
      sim.path = route;
      sim.segIdx = 0;
      sim.t = 0;
      if (sim.def.estado !== "CHARGING") sim.def.estado = "REROUTING";
    }

    const chargerId = this.chargingTarget.get(sim.def.id);
    if (sim.def.estado === "CHARGING" && chargerId) {
      const charger = this.layout.nodes.find((n) => n.id === chargerId);
      if (
        charger &&
        this.dist(sim.def.x, sim.def.y, charger.x, charger.y) < 25
      ) {
        sim.def.bateria = Math.min(100, sim.def.bateria + 0.35);
        if (sim.def.bateria >= 90) {
          sim.def.estado = "IDLE";
          this.chargingTarget.delete(sim.def.id);
        }
        return;
      }
    }

    let toIdx = sim.segIdx + sim.dir;
    if (toIdx < 0 || toIdx > sim.path.length - 1) {
      sim.dir = (sim.dir * -1) as 1 | -1; // invertir en el extremo para no salir del path
      toIdx = sim.segIdx + sim.dir;
    }
    const fromId = sim.path[sim.segIdx];
    const toId = sim.path[toIdx];
    if (this.isBlocked(fromId, toId)) {
      if (sim.def.estado !== "CHARGING") sim.def.estado = "REROUTING";
      sim.path = this.routeFor(sim);
      sim.segIdx = 0;
      sim.t = 0;
      return;
    }

    const from = this.node(fromId);
    const to = this.node(toId);

    let nearPed = false;
    for (const p of this.pedState) {
      if (this.dist(sim.def.x, sim.def.y, p.x, p.y) < p.radius * 4 + 15) {
        nearPed = true;
        break;
      }
    }
    if (nearPed && sim.waitTicks < 8) {
      // Paciencia anti-atasco: espera razonable (~1.6 s reales) y luego avanza con cuidado
      sim.waitTicks += 1;
      if (sim.def.estado !== "CHARGING") sim.def.estado = "WAITING_OBSTACLE";
      return;
    }
    sim.waitTicks = 0;

    if (sim.def.estado === "CHARGING") {
      // Mantener CHARGING mientras se dirige al cargador
    } else if (sim.def.estado === "REROUTING" && sim.t > 0.05) {
      sim.def.estado = "MOVING_TO_DELIVERY";
    } else if (sim.def.estado === "WAITING_OBSTACLE") {
      sim.def.estado = "MOVING_TO_DELIVERY";
    }

    // Normalizar por longitud del tramo: `speed` es en px/s real (TICK_MS=0.2 s)
    const segLen = Math.hypot(to.x - from.x, to.y - from.y) || 1;
    sim.t += (sim.speed * 0.2) / segLen;
    if (sim.t >= 1) {
      sim.t = 0;
      // Ping-pong: al llegar a un extremo invierte la dirección para no teletransportarse
      if (sim.segIdx + sim.dir < 0 || sim.segIdx + sim.dir > sim.path.length - 1) {
        sim.dir = (sim.dir * -1) as 1 | -1;
      }
      sim.segIdx += sim.dir;
      if (this.rng() < 0.02 && sim.def.tarea_asignada) {
        const m = this.missions.find((x) => x.id === sim.def.tarea_asignada);
        if (m) m.estado = "completada";
        sim.def.tarea_asignada = null;
        this.kpis.viajes_completados += 1;
        if (this.rng() < 0.6) this.kpis.viajes_vacios_evitados += 1;
      }
    }

    const t = Math.min(sim.t, 1);
    sim.def.x = from.x + (to.x - from.x) * t;
    sim.def.y = from.y + (to.y - from.y) * t;
    sim.def.angulo =
      (Math.atan2(to.y - from.y, to.x - from.x) * 180) / Math.PI;
    // Lookahead de ruta respetando la dirección (ping-pong)
    const ahead: string[] = [];
    let ai = sim.segIdx;
    for (let k = 0; k < 3 && ai >= 0 && ai < sim.path.length; k++) {
      ahead.push(sim.path[ai]);
      ai += sim.dir;
    }
    sim.def.path = ahead;

    if (sim.def.estado === "CHARGING") {
      sim.def.bateria = Math.max(10, sim.def.bateria - 0.01);
    } else {
      sim.def.bateria = Math.max(10, sim.def.bateria - 0.02);
      if (sim.def.bateria < 20) sim.def.estado = "CHARGING";
    }
  }

  private advancePed(p: typeof this.pedState[0]) {
    const fromId = p.waypoints[p.wpIdx];
    const toId = p.waypoints[(p.wpIdx + 1) % p.waypoints.length];
    const from = this.node(fromId);
    const to = this.node(toId);
    const segLen = Math.hypot(to.x - from.x, to.y - from.y) || 1;
    p.t += (p.speed * 0.2) / segLen; // speed en px/s reales; normalizado por longitud del tramo
    if (p.t >= 1) {
      p.t = 0;
      p.wpIdx = (p.wpIdx + 1) % p.waypoints.length;
    }
    const t = Math.min(p.t, 1);
    p.x = from.x + (to.x - from.x) * t;
    p.y = from.y + (to.y - from.y) * t;
  }

  step(): SimulationSnapshot {
    this.tickId += 1;
    this.simTime += 0.2;

    this.amrSims.forEach((s) => this.advanceAmr(s));
    this.pedState.forEach((p) => this.advancePed(p));

    if (this.tickId % 25 === 0) {
      Object.values(this.lineLevels).forEach((l) => {
        l.nivel_pct = Math.max(5, l.nivel_pct - 0.3 - this.rng() * 0.5);
        l.minutos_restantes = Math.max(1, l.minutos_restantes - 0.2);
        if (l.nivel_pct < 25 && this.rng() < 0.25) {
          this.missions.unshift({
            id: `TSK_peak_${this.tickId}`,
            tipo: "SUPPLY_REQUEST",
            origen: "WH_MP_1",
            destino: "E1_IN",
            prioridad: 10,
            estado: "pendiente",
            amr_asignado: null,
          });
          this.kpis.paradas_evitadas += 1;
        }
      });
      this.missions.forEach((m) => {
        if (m.estado === "pendiente" && this.rng() < 0.08) m.estado = "asignada";
        if (m.estado === "asignada" && this.rng() < 0.12) m.estado = "en_curso";
      });
      if (this.missions.length > 10) this.missions.pop();
    }

    const obstacles: SimulationSnapshot["obstacles"] = this.pedState.map((p) => ({
      id: p.id,
      tipo: "OPERATOR" as TipoObstaculo,
      x: p.x,
      y: p.y,
      radius: p.radius,
      edge: null,
    }));

    this.blocked.forEach((key) => {
      const [a, b] = key.split("-");
      const na = this.node(a);
      const nb = this.node(b);
      obstacles.push({
        id: `BLK_${key}`,
        tipo: "SPILL",
        x: (na.x + nb.x) / 2,
        y: (na.y + nb.y) / 2,
        radius: 0,
        edge: [a, b],
      });
    });

    const notices =
      this.pendingNotices.length > 0 ? [...this.pendingNotices] : undefined;
    this.pendingNotices = [];

    return {
      sim_time: this.simTime,
      tick_id: this.tickId,
      amrs: this.amrSims.map((s) => ({ ...s.def })),
      lines: Object.entries(this.lineLevels).map(([id, l]) => ({
        id,
        nombre: l.nombre,
        material: l.material,
        nivel_pct: l.nivel_pct,
        minutos_restantes: l.minutos_restantes,
      })),
      obstacles,
      kpis: { ...this.kpis },
      notices,
      out_stock: {},
    };
  }
}
