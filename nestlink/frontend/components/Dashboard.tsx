"use client";

import { useCallback, useEffect, useState } from "react";
import { ControlPanel } from "@/components/ControlPanel";
import { FleetBatteryPanel } from "@/components/FleetBatteryPanel";
import { FleetChatWidget } from "@/components/FleetChatWidget";
import { FleetDetailView } from "@/components/FleetDetailView";
import { FloatingDetailModal } from "@/components/FloatingDetailModal";
import { FloatingLinesBar } from "@/components/FloatingLinesBar";
import { Header } from "@/components/Header";
import { KanbanDetailView } from "@/components/KanbanDetailView";
import { KanbanPanel } from "@/components/KanbanPanel";
import { KpiMiniPanel } from "@/components/KpiMiniPanel";
import { LineGaugesPanel } from "@/components/LineGaugesPanel";
import { NoticeBanner } from "@/components/NoticeBanner";
import { PlantMap } from "@/components/PlantMap";
import { TrendsPanel } from "@/components/TrendsPanel";
import { usePlantLayout } from "@/hooks/usePlantLayout";
import { useLerpAmrs, useSimulation } from "@/hooks/useSimulation";
import { useToast } from "@/hooks/useToast";
import type { KPIsState, SelectedEdge, SpillMode } from "@/lib/types";

const EMPTY_KPIS: KPIsState = {
  viajes_completados: 0,
  viajes_vacios_evitados: 0,
  paradas_evitadas: 0,
  tiempo_medio_entrega_min: 0,
  km_evitados: 0,
  roi_km_pct: 0,
  tiempo_medio_en_out_min: 0,
};

export function Dashboard() {
  const { pushToast } = useToast();
  const {
    plants,
    selectedPlantId,
    changePlant,
    layout,
    layoutKey,
    error: layoutError,
    loading: plantLoading,
  } = usePlantLayout();

  const {
    snapshot,
    missions,
    mode,
    blockEdge,
    unblockEdge,
    injectPeak,
    simulateLowBattery,
    refill,
    resetMissions,
    adjustMissions,
  } = useSimulation(layout);

  const renderAmrs = useLerpAmrs(snapshot, layoutKey);

  const [spillMode, setSpillMode] = useState<SpillMode>("none");
  const [selectedEdge, setSelectedEdge] = useState<SelectedEdge | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [lowBatteryLoadingId, setLowBatteryLoadingId] = useState<string | null>(
    null
  );
  const [fleetCollapsed, setFleetCollapsed] = useState(false);
  const [linesCollapsed, setLinesCollapsed] = useState(true);
  const [kanbanCollapsed, setKanbanCollapsed] = useState(false);
  const [fleetModalOpen, setFleetModalOpen] = useState(false);
  const [kanbanModalOpen, setKanbanModalOpen] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [lidarMode, setLidarMode] = useState(false);
  /** Capa Wi-Fi: default OFF para no distraer; se enciende en el slide de red */
  const [showWifiNetwork, setShowWifiNetwork] = useState(false);

  // Default ON en planta realistic (pitch LiDAR)
  useEffect(() => {
    setLidarMode(selectedPlantId === "realistic");
  }, [selectedPlantId]);

  const sidebarNarrow =
    fleetCollapsed && linesCollapsed && kanbanCollapsed ? "72px" : "240px";

  useEffect(() => {
    if (!fullscreen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setFullscreen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [fullscreen]);

  const handleSpillModeChange = (mode: SpillMode) => {
    setSpillMode(mode);
    setSelectedEdge(null);
  };

  const handleConfirmBlock = useCallback(async () => {
    if (!selectedEdge) return;
    setActionLoading(true);
    const label = `${selectedEdge.from}–${selectedEdge.to}`;
    try {
      await blockEdge(selectedEdge.from, selectedEdge.to);
      pushToast(`Derrame bloqueado en ${label}`, "success");
      setSelectedEdge(null);
      setSpillMode("none");
    } catch {
      pushToast(`Error al bloquear ${label}`, "error");
    } finally {
      setActionLoading(false);
    }
  }, [selectedEdge, blockEdge, pushToast]);

  const handleConfirmUnblock = useCallback(async () => {
    if (!selectedEdge) return;
    setActionLoading(true);
    const label = `${selectedEdge.from}–${selectedEdge.to}`;
    try {
      await unblockEdge(selectedEdge.from, selectedEdge.to);
      pushToast(`Pasillo despejado: ${label}`, "success");
      setSelectedEdge(null);
      setSpillMode("none");
    } catch {
      pushToast(`Error al despejar ${label}`, "error");
    } finally {
      setActionLoading(false);
    }
  }, [selectedEdge, unblockEdge, pushToast]);

  const handlePeak = useCallback(
    async (lineId: string, label: string) => {
      setActionLoading(true);
      try {
        await injectPeak(lineId);
        pushToast(`Pico de demanda en ${label}`, "success");
      } catch {
        pushToast(`Error al inyectar pico en ${label}`, "error");
      } finally {
        setActionLoading(false);
      }
    },
    [injectPeak, pushToast]
  );

  const handleRefill = useCallback(
    async (lineId?: string | null) => {
      setActionLoading(true);
      try {
        const result = await refill(lineId, 80);
        const scheduled = result?.lines ?? [];
        const label =
          scheduled.length > 0
            ? scheduled.join(", ")
            : lineId ?? "empacadoras";
        pushToast(`⌛ Metas >80% fijadas: ${label}`, "success");
      } catch {
        pushToast("Error al programar refill", "error");
      } finally {
        setActionLoading(false);
      }
    },
    [refill, pushToast]
  );

  const handleResetMissions = useCallback(async () => {
    setActionLoading(true);
    try {
      const result = await resetMissions();
      const activas = Array.isArray(result.activas) ? result.activas.length : (result.activas ?? 0);
      pushToast(
        `Misiones reiniciadas (${activas} activas)`,
        "success"
      );
    } catch (e) {
      const msg = e instanceof Error ? e.message : "";
      if (msg.includes("Solo disponible con backend")) {
        pushToast("Solo disponible con backend", "info");
      } else {
        pushToast("Error al reiniciar misiones", "error");
      }
    } finally {
      setActionLoading(false);
    }
  }, [resetMissions, pushToast]);

  const handleAdjustMissions = useCallback(
    async (delta: number) => {
      setActionLoading(true);
      try {
        const result = await adjustMissions(delta);
        const sign = delta > 0 ? `+${delta}` : `${delta}`;
        const action = delta > 0 ? "encoladas" : "";
        pushToast(
          `${sign} misiones${action ? ` ${action}` : ""} (${result.pendientes} pendientes)`,
          "success"
        );
      } catch (e) {
        const msg = e instanceof Error ? e.message : "";
        if (msg.includes("Solo disponible con backend")) {
          pushToast("Solo disponible con backend", "info");
        } else {
          pushToast("Error al ajustar misiones", "error");
        }
      } finally {
        setActionLoading(false);
      }
    },
    [adjustMissions, pushToast]
  );

  const handleLowBattery = useCallback(
    async (amrId: string, nombre: string) => {
      setLowBatteryLoadingId(amrId);
      try {
        await simulateLowBattery(amrId);
        pushToast(`${nombre}: batería simulada al 15% → recarga`, "success");
      } catch {
        pushToast(`Error al simular batería baja en ${nombre}`, "error");
      } finally {
        setLowBatteryLoadingId(null);
      }
    },
    [simulateLowBattery, pushToast]
  );

  const handlePlantChange = useCallback(
    async (plantId: string) => {
      pushToast(`Cambiando a planta ${plantId}…`, "info");
      try {
        await changePlant(plantId);
        setSelectedEdge(null);
        setSpillMode("none");
        pushToast(
          `Planta activa: ${plants.find((p) => p.id === plantId)?.nombre ?? plantId}`,
          "success"
        );
      } catch {
        pushToast("Error al cambiar planta", "error");
      }
    },
    [changePlant, plants, pushToast]
  );

  if (layoutError && !layout) {
    return (
      <div className="p-8 text-nest-red">
        Error cargando layout: {layoutError}
      </div>
    );
  }

  if (!layout) {
    return (
      <div className="nest-shell flex h-screen flex-col items-center justify-center gap-3 text-nest-muted">
        <div
          className="h-8 w-8 rounded-full border-2 border-black/[0.08] border-t-nest-accent animate-spin"
          aria-hidden
        />
        <p className="text-sm">Cargando mapa de planta…</p>
      </div>
    );
  }

  const kpis = snapshot?.kpis ?? EMPTY_KPIS;
  const lines = snapshot?.lines ?? [];
  const obstacles = snapshot?.obstacles ?? [];
  const notices = snapshot?.notices ?? [];
  const fleetAmrs = snapshot?.amrs ?? [];

  const mapEl = (
    <PlantMap
      layout={layout}
      layoutKey={layoutKey}
      amrs={renderAmrs}
      missions={missions}
      obstacles={obstacles}
      spillMode={spillMode}
      selectedEdge={selectedEdge}
      onEdgeSelect={setSelectedEdge}
      interactive={fullscreen}
      plantId={selectedPlantId}
      lidarMode={lidarMode}
      simTime={snapshot?.sim_time ?? 0}
      outStock={snapshot?.out_stock}
      showWifiNetwork={showWifiNetwork}
    />
  );

  if (fullscreen) {
    return (
      <div className="nest-shell relative flex h-screen w-screen flex-col text-nest-text overflow-hidden">
        <Header
          simTime={snapshot?.sim_time}
          amrCount={renderAmrs.length}
          mode={mode}
          plants={plants}
          selectedPlantId={selectedPlantId}
          onPlantChange={handlePlantChange}
          plantLoading={plantLoading}
          fullscreen
          onToggleFullscreen={() => setFullscreen(false)}
        />
        <div className="relative flex-1 min-h-0 min-w-0">
          <div className="absolute inset-0 overflow-hidden">{mapEl}</div>
          <FloatingLinesBar
            lines={lines}
            onClose={() => setFullscreen(false)}
            onPeak={(id, label) => {
              void handlePeak(id, label);
            }}
            onRefill={(id) => {
              void handleRefill(id);
            }}
            loading={actionLoading}
          />
        </div>
        <FleetChatWidget />
      </div>
    );
  }

  return (
    <div className="nest-shell flex h-screen flex-col text-nest-text">
      <Header
        simTime={snapshot?.sim_time}
        amrCount={renderAmrs.length}
        mode={mode}
        plants={plants}
        selectedPlantId={selectedPlantId}
        onPlantChange={handlePlantChange}
        plantLoading={plantLoading}
        fullscreen={false}
        onToggleFullscreen={() => setFullscreen(true)}
      />
      <NoticeBanner notices={notices} />
      <div
        className="dashboard-grid grid flex-1 gap-2 p-3 min-h-0 transition-[grid-template-columns] duration-300"
        style={{
          gridTemplateColumns: `1fr ${sidebarNarrow}`,
          gridTemplateRows: "minmax(0, 1fr)",
        }}
      >
        <div className="relative flex flex-col gap-1.5 min-h-0 min-w-0">
          <ControlPanel
            spillMode={spillMode}
            onSpillModeChange={handleSpillModeChange}
            selectedEdge={selectedEdge}
            onConfirmBlock={handleConfirmBlock}
            onConfirmUnblock={handleConfirmUnblock}
            lines={lines}
            onPeak={handlePeak}
            onRefill={(lineId) => handleRefill(lineId)}
            onRefillAll={() => handleRefill(null)}
            onResetMissions={handleResetMissions}
            onAdjustMissions={handleAdjustMissions}
            offline={mode === "offline"}
            loading={actionLoading}
            lidarMode={lidarMode}
            onLidarModeChange={setLidarMode}
            showWifiNetwork={showWifiNetwork}
            onShowWifiNetworkChange={setShowWifiNetwork}
          />
          <div className="nest-panel relative flex-1 min-h-0 min-w-0 overflow-hidden shadow-nest-glow">
            {mapEl}
            <button
              type="button"
              onClick={() => setFullscreen(true)}
              className="absolute top-2 right-2 z-10 nest-btn-ghost nest-btn px-2 py-1 text-[0.65rem] bg-white/90 backdrop-blur-sm shadow-nest-panel"
              title="Abrir mapa en página única"
            >
              ⛶ Ampliar
            </button>
          </div>
        </div>

        <div className="flex h-full min-h-0 flex-col gap-1.5 overflow-hidden">
          <KpiMiniPanel kpis={kpis} />
          <FleetBatteryPanel
            amrs={fleetAmrs}
            onLowBattery={handleLowBattery}
            loadingId={lowBatteryLoadingId}
            collapsed={fleetCollapsed}
            onToggle={() => setFleetCollapsed((c) => !c)}
            onExpand={() => setFleetModalOpen(true)}
          />
          <LineGaugesPanel
            lines={lines}
            collapsed={linesCollapsed}
            onToggle={() => setLinesCollapsed((c) => !c)}
          />
          <KanbanPanel
            missions={missions}
            collapsed={kanbanCollapsed}
            onToggle={() => setKanbanCollapsed((c) => !c)}
            onExpand={() => setKanbanModalOpen(true)}
          />
          {!fleetCollapsed && !linesCollapsed && !kanbanCollapsed && (
            <div className="shrink-0">
              <TrendsPanel />
            </div>
          )}
        </div>
      </div>

      <FloatingDetailModal
        title="Flota — Vista detallada"
        open={fleetModalOpen}
        onClose={() => setFleetModalOpen(false)}
      >
        <FleetDetailView
          amrs={fleetAmrs}
          layout={layout}
          onLowBattery={handleLowBattery}
          loadingId={lowBatteryLoadingId}
        />
      </FloatingDetailModal>

      <FloatingDetailModal
        title="Kanban — Vista detallada"
        open={kanbanModalOpen}
        onClose={() => setKanbanModalOpen(false)}
      >
        <KanbanDetailView missions={missions} />
      </FloatingDetailModal>

      <FleetChatWidget />
    </div>
  );
}
