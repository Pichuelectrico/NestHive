"use client";

import { CollapsibleSidePanel } from "@/components/CollapsibleSidePanel";
import { AMR_STATE_COLORS } from "@/lib/amrColors";
import type { AMRState } from "@/lib/types";

interface FleetBatteryPanelProps {
  amrs: AMRState[];
  onLowBattery: (amrId: string, nombre: string) => Promise<void>;
  loadingId: string | null;
  collapsed: boolean;
  onToggle: () => void;
  onExpand: () => void;
}

function batteryBarColor(pct: number): string {
  if (pct <= 25) return "#f87171";
  if (pct <= 50) return "#fbbf24";
  return "#34d399";
}

function batteryEmoji(amr: AMRState): string {
  if (amr.estado === "CHARGING") return "⚡";
  if (amr.bateria <= 25) return "🪫";
  if (amr.bateria <= 50) return "🔋";
  return "🔋";
}

function estadoLabel(estado: string): string {
  return estado.replace(/_/g, " ");
}

export function FleetBatteryPanel({
  amrs,
  onLowBattery,
  loadingId,
  collapsed,
  onToggle,
  onExpand,
}: FleetBatteryPanelProps) {
  return (
    <CollapsibleSidePanel
      title="Flota — Batería"
      collapsed={collapsed}
      onToggle={onToggle}
      onExpand={onExpand}
    >
      {amrs.length === 0 && (
        <p className="text-xs text-nest-muted">Sin AMRs en snapshot</p>
      )}
      <div className="space-y-2">
        {amrs.map((amr) => {
          const ring = AMR_STATE_COLORS[amr.estado] ?? "#8b9aad";
          const barColor = batteryBarColor(amr.bateria);
          return (
            <div key={amr.id} className="nest-card p-2.5 text-xs">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="w-2 h-2 rounded-full shrink-0 ring-2 ring-white/10"
                    style={{ background: ring, boxShadow: `0 0 8px ${ring}55` }}
                    title={estadoLabel(amr.estado)}
                  />
                  <span className="font-medium truncate text-nest-text">
                    {amr.nombre}
                  </span>
                </div>
                <button
                  type="button"
                  disabled={loadingId === amr.id}
                  onClick={() => onLowBattery(amr.id, amr.nombre)}
                  className="nest-btn-ghost nest-btn px-2 py-0.5 text-[0.65rem]"
                  title="Simular 15% batería"
                >
                  15% test
                </button>
              </div>
              <div className="mt-1 text-[0.65rem] text-nest-muted capitalize">
                {estadoLabel(amr.estado)}
              </div>
              <div className="mt-2 h-1.5 rounded-full bg-black/10 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${Math.max(0, Math.min(100, amr.bateria))}%`,
                    background: `linear-gradient(90deg, ${barColor}aa, ${barColor})`,
                  }}
                />
              </div>
              <div className="mt-1 flex justify-between text-[0.65rem] text-nest-muted font-mono tabular-nums">
                <span>{batteryEmoji(amr)} {amr.bateria}%</span>
                {amr.tarea_asignada && (
                  <span className="truncate ml-2 text-nest-accent">
                    {amr.tarea_asignada}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </CollapsibleSidePanel>
  );
}
