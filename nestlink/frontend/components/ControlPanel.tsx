"use client";

import { useEffect, useState } from "react";
import type { AMRState, LineaState, SelectedEdge, SpillMode } from "@/lib/types";

interface ControlPanelProps {
  spillMode: SpillMode;
  onSpillModeChange: (mode: SpillMode) => void;
  selectedEdge: SelectedEdge | null;
  onConfirmBlock: () => Promise<void>;
  onConfirmUnblock: () => Promise<void>;
  lines: LineaState[];
  onPeak: (lineId: string, label: string) => Promise<void>;
  onRefill: (lineId: string) => Promise<void>;
  onRefillAll: () => Promise<void>;
  onResetMissions: () => Promise<void>;
  onAdjustMissions: (delta: number) => Promise<void>;
  offline: boolean;
  loading: boolean;
  lidarMode?: boolean;
  onLidarModeChange?: (on: boolean) => void;
  /** Capa APs Wi-Fi en el mapa (default OFF) */
  showWifiNetwork?: boolean;
  onShowWifiNetworkChange?: (on: boolean) => void;
  onEmergencyPickup?: (line: string) => Promise<void>;
  agvs?: AMRState[];
  onBreakdown?: (id: string, name: string) => Promise<void>;
  breakdownLoadingId?: string | null;
}

export function ControlPanel({
  spillMode,
  onSpillModeChange,
  selectedEdge,
  onConfirmBlock,
  onConfirmUnblock,
  lines,
  onPeak,
  onRefill,
  onRefillAll,
  onResetMissions,
  onAdjustMissions,
  offline,
  loading,
  lidarMode = false,
  onLidarModeChange,
  showWifiNetwork = false,
  onShowWifiNetworkChange,
  onEmergencyPickup,
  agvs = [],
  onBreakdown,
  breakdownLoadingId,
}: ControlPanelProps) {
  const [peakLineId, setPeakLineId] = useState("");
  const [selectedAgvId, setSelectedAgvId] = useState("");
  const fleetAgvs = agvs;
  const activeAgv = fleetAgvs.find((amr) => amr.id === selectedAgvId) ?? fleetAgvs[0];
  const packingLines = lines.filter(
    (l) => l.is_packing ?? l.id.startsWith("E")
  );

  useEffect(() => {
    if (packingLines.length && !peakLineId) {
      setPeakLineId(packingLines[0].id);
    }
    if (packingLines.length && !packingLines.some((l) => l.id === peakLineId)) {
      setPeakLineId(packingLines[0].id);
    }
  }, [packingLines, peakLineId]);

  const toggleMode = (mode: SpillMode) => {
    if (spillMode === mode) onSpillModeChange("none");
    else onSpillModeChange(mode);
  };

  const selectedLine = packingLines.find((l) => l.id === peakLineId);
  const needsConfirm = spillMode !== "none";

  return (
    <div className="nest-panel shrink-0 px-2 py-1.5 space-y-1.5">
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="nest-label shrink-0 px-1 hidden sm:inline">Ops</span>

        <button
          type="button"
          onClick={() => toggleMode("block")}
          title="Modo derrame"
          className={`nest-btn ${
            spillMode === "block" ? "nest-btn-warm" : "nest-btn-ghost"
          }`}
        >
          🚧 Derrame
        </button>
        <button
          type="button"
          onClick={() => toggleMode("unblock")}
          title="Modo despeje"
          className={`nest-btn ${
            spillMode === "unblock" ? "nest-btn-primary" : "nest-btn-ghost"
          }`}
        >
          ✅ Despeje
        </button>

        {onLidarModeChange && (
          <button
            type="button"
            onClick={() => onLidarModeChange(!lidarMode)}
            title="Vista LiDAR — rutas como barrido SLAM"
            className={`nest-btn ${
              lidarMode ? "nest-btn-primary" : "nest-btn-ghost"
            }`}
            aria-pressed={lidarMode}
          >
            {lidarMode ? "📡 LiDAR ON" : "📡 LiDAR"}
          </button>
        )}

        {onShowWifiNetworkChange && (
          <button
            type="button"
            onClick={() => onShowWifiNetworkChange(!showWifiNetwork)}
            title="Mostrar APs / cobertura Wi-Fi industrial"
            className={`nest-btn ${
              showWifiNetwork ? "nest-btn-primary" : "nest-btn-ghost"
            }`}
            aria-pressed={showWifiNetwork}
          >
            {showWifiNetwork ? "📶 Red ON" : "📶 Mostrar red"}
          </button>
        )}

        <span className="hidden sm:inline h-5 w-px bg-black/[0.1] mx-0.5" aria-hidden />

        {packingLines.length > 0 && (
          <>
            <select
              value={peakLineId}
              onChange={(e) => setPeakLineId(e.target.value)}
              className="nest-select min-w-[110px] max-w-[160px] text-xs py-1"
              aria-label="Línea de producción"
            >
              {packingLines.map((l) => (
                <option key={l.id} value={l.id} className="bg-white text-nest-text">
                  {l.nombre}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={loading || !peakLineId}
              onClick={() =>
                onPeak(peakLineId, selectedLine?.nombre ?? peakLineId)
              }
              className="nest-btn-warm"
              title="Inyectar pico de demanda"
            >
              Pico
            </button>
            <button
              type="button"
              disabled={loading || !peakLineId}
              onClick={() => onRefill(peakLineId)}
              className="nest-btn-success"
              title="Rellenar línea al 80%"
            >
              80%
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => onRefillAll()}
              className="nest-btn-ghost"
              title="Rellenar todas al 80%"
            >
              Todas
            </button>
          </>
        )}

        <span className="hidden md:inline h-5 w-px bg-black/[0.1] mx-0.5" aria-hidden />

        <button
          type="button"
          disabled={loading}
          onClick={() => onResetMissions()}
          className="nest-btn-ghost"
          title="Reiniciar tareas"
        >
          Reset
        </button>
        <button
          type="button"
          disabled={loading}
          onClick={() => onAdjustMissions(5)}
          className="nest-btn-success"
          title="+5 misiones"
        >
          +5
        </button>
        <button
          type="button"
          disabled={loading}
          onClick={() => onAdjustMissions(-5)}
          className="nest-btn-warning"
          title="−5 misiones"
        >
          −5
        </button>

        {offline && (
          <span className="nest-status-offline ml-auto text-[0.65rem]">
            Sin backend
          </span>
        )}
      </div>
      {onEmergencyPickup && <div className="flex items-center gap-1 border border-red-500/30 rounded px-1.5 py-1">
        <span className="text-[0.65rem] text-red-700">🚨 Emergencia</span>
        {(["R1", "R2", "R3"] as const).map((line) => <button key={line} type="button" disabled={loading || offline} onClick={() => void onEmergencyPickup(line)} aria-label={`Disparar emergencia de recolección ${line}`} className="nest-btn nest-btn-ghost border-red-500/40 text-red-700 px-2 py-0.5">{line}</button>)}
      </div>}

      {onBreakdown && (
        <div className="flex flex-wrap items-center gap-1.5 rounded-lg border border-red-600/25 bg-red-50/70 px-2 py-1.5">
          <span className="text-[0.65rem] font-bold uppercase tracking-wide text-red-800">Avería AMR</span>
          <select
            value={activeAgv?.id ?? ""}
            onChange={(e) => setSelectedAgvId(e.target.value)}
            disabled={!fleetAgvs.length || offline}
            aria-label="AMR para simular avería"
            className="nest-select min-w-0 flex-1 py-1 text-xs"
          >
            {fleetAgvs.length === 0 && <option value="">Sin AMR</option>}
            {fleetAgvs.map((agv) => <option key={agv.id} value={agv.id}>{agv.nombre}</option>)}
          </select>
          <button
            type="button"
            disabled={offline || !activeAgv || activeAgv.estado === "ERROR" || Boolean(breakdownLoadingId)}
            onClick={() => activeAgv && void onBreakdown(activeAgv.id, activeAgv.nombre)}
            className="nest-btn-danger"
          >
            {breakdownLoadingId ? "Simulando…" : "Simular avería"}
          </button>
        </div>
      )}

      {needsConfirm && spillMode === "block" && (
        <div className="nest-hint nest-hint-warm text-xs py-1.5">
          <span>Selecciona un pasillo en el mapa</span>
          {selectedEdge && (
            <>
              <span className="font-mono text-orange-800">
                {selectedEdge.from} → {selectedEdge.to}
              </span>
              <button
                type="button"
                disabled={loading}
                onClick={() => onConfirmBlock()}
                className="nest-btn-danger"
              >
                Confirmar
              </button>
            </>
          )}
        </div>
      )}

      {needsConfirm && spillMode === "unblock" && (
        <div className="nest-hint nest-hint-info text-xs py-1.5">
          <span>Clic en pasillo bloqueado (rojo)</span>
          {selectedEdge && (
            <>
              <span className="font-mono text-nest-ink">
                {selectedEdge.from} → {selectedEdge.to}
              </span>
              <button
                type="button"
                disabled={loading}
                onClick={() => onConfirmUnblock()}
                className="nest-btn-primary"
              >
                Confirmar
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
