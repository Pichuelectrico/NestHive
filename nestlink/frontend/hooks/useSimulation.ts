"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  checkBackendHealth,
  fetchMissions,
  parseSnapshot,
} from "@/lib/api";
import { IS_STATIC_PAGES, WS_URL } from "@/lib/config";
import { DemoEngine } from "@/lib/demoEngine";
import type {
  AMRRenderState,
  ConnectionMode,
  Mission,
  PlantLayout,
  SimulationSnapshot,
} from "@/lib/types";

const TICK_MS = 200;

export function useSimulation(layout: PlantLayout | null) {
  const [snapshot, setSnapshot] = useState<SimulationSnapshot | null>(null);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [mode, setMode] = useState<ConnectionMode>("connecting");
  const demoRef = useRef<DemoEngine | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refreshMissions = useCallback(async () => {
    if (mode === "offline" && demoRef.current) {
      setMissions(demoRef.current.getMissions());
      return;
    }
    const m = await fetchMissions();
    if (m.length) setMissions(m);
  }, [mode]);

  // Iniciar conexión o modo offline
  useEffect(() => {
    if (!layout) return;

    let disposed = false;

    async function connect() {
      // Despliegue estático (GitHub Pages): no hay backend → DemoEngine directo,
      // sin esperar health-check ni abrir WebSocket.
      if (IS_STATIC_PAGES) {
        startOffline();
        return;
      }
      const healthy = await checkBackendHealth();
      if (disposed) return;

      if (healthy) {
        setMode("connecting");
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!disposed) setMode("live");
        };

        ws.onmessage = (ev) => {
          try {
            const parsed = parseSnapshot(JSON.parse(ev.data));
            if (parsed) setSnapshot(parsed);
          } catch {
            // ignorar tramas inválidas
          }
        };

        ws.onerror = () => {
          if (!disposed) startOffline();
        };

        ws.onclose = () => {
          if (!disposed && mode === "live") startOffline();
        };
      } else {
        startOffline();
      }
    }

    function startOffline() {
      if (disposed) return;
      wsRef.current?.close();
      demoRef.current = new DemoEngine(layout!);
      setMode("offline");
      setMissions(demoRef.current.getMissions());

      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = setInterval(() => {
        if (demoRef.current) {
          const snap = demoRef.current.step();
          setSnapshot(snap);
          setMissions(demoRef.current.getMissions());
        }
      }, TICK_MS);
    }

    connect();

    return () => {
      disposed = true;
      wsRef.current?.close();
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [layout]);

  // Refrescar misiones REST en modo live al cambiar tick
  useEffect(() => {
    if (mode !== "live" || !snapshot) return;
    refreshMissions();
  }, [mode, snapshot?.tick_id, refreshMissions]);

  const blockEdge = useCallback(
    async (from: string, to: string) => {
      if (mode === "offline" && demoRef.current) {
        demoRef.current.toggleBlock(from, to);
        return;
      }
      const { blockEdge: apiBlock } = await import("@/lib/api");
      await apiBlock(from, to);
    },
    [mode]
  );

  const unblockEdge = useCallback(
    async (from: string, to: string) => {
      if (mode === "offline" && demoRef.current) {
        demoRef.current.toggleBlock(from, to);
        return;
      }
      const { unblockEdge: apiUnblock } = await import("@/lib/api");
      await apiUnblock(from, to);
    },
    [mode]
  );

  const injectPeak = useCallback(
    async (lineId: string) => {
      if (mode === "offline" && demoRef.current) {
        demoRef.current.injectPeak(lineId);
        setMissions(demoRef.current.getMissions());
        return;
      }
      const { injectPeak: apiPeak } = await import("@/lib/api");
      await apiPeak(lineId);
    },
    [mode]
  );

  const simulateLowBattery = useCallback(
    async (amrId: string) => {
      if (mode === "offline" && demoRef.current) {
        demoRef.current.simulateLowBattery(amrId);
        return;
      }
      const { simulateLowBattery: apiLow } = await import("@/lib/api");
      await apiLow(amrId);
    },
    [mode]
  );

  const refill = useCallback(
    async (lineId?: string | null, targetPct = 80) => {
      if (mode === "offline" && demoRef.current) {
        const lines = demoRef.current.simulateRefill(lineId, targetPct);
        setMissions(demoRef.current.getMissions());
        return { lines, target_pct: targetPct };
      }
      const { refillLine } = await import("@/lib/api");
      const result = await refillLine(lineId, targetPct);
      return result;
    },
    [mode]
  );

  const resetMissionsAction = useCallback(async () => {
    if (mode === "offline") {
      throw new Error("Solo disponible con backend");
    }
    const { resetMissions: apiReset } = await import("@/lib/api");
    const result = await apiReset();
    await refreshMissions();
    return result;
  }, [mode, refreshMissions]);

  const adjustMissionsAction = useCallback(
    async (delta: number) => {
      if (mode === "offline") {
        throw new Error("Solo disponible con backend");
      }
      const { adjustMissions: apiAdjust } = await import("@/lib/api");
      const result = await apiAdjust(delta);
      await refreshMissions();
      return result;
    },
    [mode, refreshMissions]
  );

  return {
    snapshot,
    missions,
    mode,
    blockEdge,
    unblockEdge,
    injectPeak,
    simulateLowBattery,
    refill,
    resetMissions: resetMissionsAction,
    adjustMissions: adjustMissionsAction,
  };
}

/** Interpolación LERP a 60fps entre snapshots WS (5 Hz) */
export function useLerpAmrs(
  snapshot: SimulationSnapshot | null,
  resetKey = 0
): AMRRenderState[] {
  const [renderAmrs, setRenderAmrs] = useState<AMRRenderState[]>([]);
  const targetRef = useRef<SimulationSnapshot | null>(null);
  const displayRef = useRef<Map<string, { x: number; y: number }>>(new Map());
  const rafRef = useRef<number>(0);

  // Reset interpolación al cambiar planta o layout
  useEffect(() => {
    displayRef.current.clear();
    setRenderAmrs([]);
  }, [resetKey]);

  useEffect(() => {
    targetRef.current = snapshot;
    if (!snapshot) {
      setRenderAmrs([]);
      return;
    }

    snapshot.amrs.forEach((a) => {
      if (!displayRef.current.has(a.id)) {
        displayRef.current.set(a.id, { x: a.x, y: a.y });
      }
    });
  }, [snapshot]);

  useEffect(() => {
    const LERP_FACTOR = 0.15;

    const tick = () => {
      const target = targetRef.current;
      if (target) {
        const next: AMRRenderState[] = target.amrs.map((a) => {
          const cur = displayRef.current.get(a.id) ?? { x: a.x, y: a.y };
          const nx = cur.x + (a.x - cur.x) * LERP_FACTOR;
          const ny = cur.y + (a.y - cur.y) * LERP_FACTOR;
          displayRef.current.set(a.id, { x: nx, y: ny });
          return { ...a, renderX: nx, renderY: ny };
        });
        setRenderAmrs(next);
      }
      rafRef.current = requestAnimationFrame(tick);
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, []);

  return renderAmrs;
}
