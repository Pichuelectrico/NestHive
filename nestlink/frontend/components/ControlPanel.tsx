"use client";

import {
  ArrowCounterClockwise,
  Broadcast,
  CheckCircle,
  Lightning,
  Minus,
  Plus,
  Siren,
  Stack,
  Warning,
  WifiHigh,
  Wrench,
} from "@phosphor-icons/react";
import { useEffect, useState, type ReactNode } from "react";
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

function Group({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="nest-tile" aria-label={title}>
      <h3 className="nest-section-title">{title}</h3>
      <div className="space-y-2">{children}</div>
    </section>
  );
}

function Toggle({
  pressed,
  onClick,
  icon,
  label,
  hint,
}: {
  pressed: boolean;
  onClick: () => void;
  icon: ReactNode;
  label: string;
  hint?: string;
}) {
  return (
    <button type="button" aria-pressed={pressed} onClick={onClick} className="nest-toggle" title={hint}>
      <span className="flex items-center gap-2">
        {icon}
        {label}
      </span>
      <span className="nest-switch" aria-hidden />
    </button>
  );
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
  const packingLines = lines.filter((l) => l.is_packing ?? l.id.startsWith("E"));

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
    <div className="space-y-3">
      {offline && (
        <div className="nest-status-offline w-full justify-center py-1 text-[0.7rem]">
          Sin backend · acciones limitadas
        </div>
      )}

      {(onLidarModeChange || onShowWifiNetworkChange) && (
        <Group title="Vista del mapa">
          {onLidarModeChange && (
            <Toggle
              pressed={lidarMode}
              onClick={() => onLidarModeChange(!lidarMode)}
              icon={<Broadcast size={16} weight="duotone" aria-hidden />}
              label="LiDAR"
              hint="Vista LiDAR — rutas como barrido SLAM"
            />
          )}
          {onShowWifiNetworkChange && (
            <Toggle
              pressed={showWifiNetwork}
              onClick={() => onShowWifiNetworkChange(!showWifiNetwork)}
              icon={<WifiHigh size={16} weight="duotone" aria-hidden />}
              label="Red Wi-Fi industrial"
              hint="Mostrar APs y cobertura Wi-Fi industrial"
            />
          )}
        </Group>
      )}

      <Group title="Pasillos">
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            aria-pressed={spillMode === "block"}
            onClick={() => toggleMode("block")}
            title="Modo derrame: bloquear un pasillo"
            className={`nest-btn ${spillMode === "block" ? "nest-btn-primary" : "nest-btn-ghost"}`}
          >
            <Warning size={14} aria-hidden />
            Derrame
          </button>
          <button
            type="button"
            aria-pressed={spillMode === "unblock"}
            onClick={() => toggleMode("unblock")}
            title="Modo despeje: liberar un pasillo"
            className={`nest-btn ${spillMode === "unblock" ? "nest-btn-primary" : "nest-btn-ghost"}`}
          >
            <CheckCircle size={14} aria-hidden />
            Despeje
          </button>
        </div>

        {needsConfirm && spillMode === "block" && (
          <div className="nest-hint nest-hint-warm text-xs" role="status">
            <span>Selecciona un pasillo en el mapa</span>
            {selectedEdge && (
              <>
                <span className="font-mono">
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
          <div className="nest-hint nest-hint-info text-xs" role="status">
            <span>Clic en un pasillo bloqueado (rojo)</span>
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
      </Group>

      {packingLines.length > 0 && (
        <Group title="Demanda de línea">
          <select
            value={peakLineId}
            onChange={(e) => setPeakLineId(e.target.value)}
            className="nest-select w-full cursor-pointer py-1.5 text-sm"
            aria-label="Línea de producción"
          >
            {packingLines.map((l) => (
              <option key={l.id} value={l.id} className="bg-nest-panel text-nest-text">
                {l.nombre}
              </option>
            ))}
          </select>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              disabled={loading || !peakLineId}
              onClick={() => onPeak(peakLineId, selectedLine?.nombre ?? peakLineId)}
              className="nest-btn-warm"
              title="Inyectar pico de demanda"
            >
              <Lightning size={14} aria-hidden />
              Pico
            </button>
            <button
              type="button"
              disabled={loading || !peakLineId}
              onClick={() => onRefill(peakLineId)}
              className="nest-btn-success"
              title="Rellenar la línea al 80%"
            >
              <Stack size={14} aria-hidden />
              Rellenar 80%
            </button>
          </div>
          <button
            type="button"
            disabled={loading}
            onClick={() => onRefillAll()}
            className="nest-btn-ghost w-full"
            title="Rellenar todas las líneas al 80%"
          >
            Rellenar todas
          </button>
        </Group>
      )}

      <Group title="Cola de misiones">
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            disabled={loading}
            onClick={() => onResetMissions()}
            className="nest-btn-ghost"
            title="Reiniciar tareas"
            aria-label="Reiniciar misiones"
          >
            <ArrowCounterClockwise size={14} aria-hidden />
            Reset
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() => onAdjustMissions(5)}
            className="nest-btn-success"
            title="Agregar 5 misiones"
            aria-label="Agregar 5 misiones"
          >
            <Plus size={14} aria-hidden />5
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={() => onAdjustMissions(-5)}
            className="nest-btn-warning"
            title="Quitar 5 misiones"
            aria-label="Quitar 5 misiones"
          >
            <Minus size={14} aria-hidden />5
          </button>
        </div>
      </Group>

      {onEmergencyPickup && (
        <Group title="Emergencia de recolección">
          <div className="grid grid-cols-3 gap-2">
            {(["R1", "R2", "R3"] as const).map((line) => (
              <button
                key={line}
                type="button"
                disabled={loading || offline}
                onClick={() => void onEmergencyPickup(line)}
                aria-label={`Disparar emergencia de recolección ${line}`}
                className="nest-btn nest-btn-danger"
              >
                <Siren size={14} aria-hidden />
                {line}
              </button>
            ))}
          </div>
        </Group>
      )}

      {onBreakdown && (
        <Group title="Avería de AMR">
          <select
            value={activeAgv?.id ?? ""}
            onChange={(e) => setSelectedAgvId(e.target.value)}
            disabled={!fleetAgvs.length || offline}
            aria-label="AMR para simular avería"
            className="nest-select w-full cursor-pointer py-1.5 text-sm"
          >
            {fleetAgvs.length === 0 && <option value="">Sin AMR</option>}
            {fleetAgvs.map((agv) => (
              <option key={agv.id} value={agv.id}>
                {agv.nombre}
              </option>
            ))}
          </select>
          <button
            type="button"
            disabled={offline || !activeAgv || activeAgv.estado === "ERROR" || Boolean(breakdownLoadingId)}
            onClick={() => activeAgv && void onBreakdown(activeAgv.id, activeAgv.nombre)}
            className="nest-btn-danger w-full"
          >
            <Wrench size={14} aria-hidden />
            {breakdownLoadingId ? "Simulando…" : "Simular avería"}
          </button>
        </Group>
      )}
    </div>
  );
}
