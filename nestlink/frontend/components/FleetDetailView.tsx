"use client";

import { AMR_STATE_COLORS } from "@/lib/amrColors";
import { nearestNodeId } from "@/lib/layoutBounds";
import type { AMRState, PlantLayout } from "@/lib/types";

interface FleetDetailViewProps {
  amrs: AMRState[];
  layout: PlantLayout;
  onLowBattery: (amrId: string, nombre: string) => Promise<void>;
  loadingId: string | null;
}

function batteryBarColor(pct: number): string {
  if (pct <= 25) return "#f85149";
  if (pct <= 50) return "#d29922";
  return "#3fb950";
}

function estadoLabel(estado: string): string {
  return estado.replace(/_/g, " ");
}

export function FleetDetailView({
  amrs,
  layout,
  onLowBattery,
  loadingId,
}: FleetDetailViewProps) {
  return (
    <div className="space-y-3">
      {amrs.length === 0 && (
        <p className="text-sm text-nest-muted">Sin AMRs en snapshot</p>
      )}
      {amrs.map((amr) => {
        const ring = AMR_STATE_COLORS[amr.estado] ?? "#8b949e";
        const barColor = batteryBarColor(amr.bateria);
        const nodeId = nearestNodeId(layout, amr.x, amr.y);
        const nextNode = amr.path[0] ?? "—";

        return (
          <div
            key={amr.id}
            className="nest-card p-3 text-sm"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className="w-3 h-3 rounded-full shrink-0"
                    style={{
                      background: ring,
                      boxShadow: `0 0 8px ${ring}`,
                    }}
                  />
                  <span className="font-bold text-base">{amr.nombre}</span>
                  <span className="font-mono text-xs text-nest-muted">
                    {amr.id}
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-nest-muted">
                  <span>
                    Estado:{" "}
                    <span className="text-nest-text capitalize">
                      {estadoLabel(amr.estado)}
                    </span>
                  </span>
                  <span>
                    Tipo:{" "}
                    <span className="text-nest-text">{amr.tipo}</span>
                  </span>
                  <span>
                    Nodo actual:{" "}
                    <span className="text-nest-text font-mono">{nodeId}</span>
                  </span>
                  <span>
                    Siguiente:{" "}
                    <span className="text-nest-text font-mono">{nextNode}</span>
                  </span>
                  <span>
                    Posición:{" "}
                    <span className="text-nest-text font-mono">
                      ({amr.x.toFixed(0)}, {amr.y.toFixed(0)})
                    </span>
                  </span>
                  <span>
                    Tarea:{" "}
                    <span className="text-nest-text">
                      {amr.tarea_asignada ?? "—"}
                    </span>
                  </span>
                </div>
              </div>
              <button
                type="button"
                disabled={loadingId === amr.id}
                onClick={() => onLowBattery(amr.id, amr.nombre)}
                className="shrink-0 rounded border border-yellow-600/50 bg-yellow-500/10 px-3 py-1.5 text-xs hover:bg-yellow-500/20 disabled:opacity-50"
              >
                🔋 Simular 15%
              </button>
            </div>
            <div className="mt-3">
              <div className="flex justify-between text-xs text-nest-muted mb-1">
                <span>Batería</span>
                <span>{amr.bateria}%</span>
              </div>
              <div className="h-3 rounded-full border border-nest-border bg-black/[0.06] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${Math.max(0, Math.min(100, amr.bateria))}%`,
                    background: barColor,
                  }}
                />
              </div>
            </div>
            {amr.path.length > 0 && (
              <div className="mt-2 text-[0.65rem] text-nest-muted">
                Ruta:{" "}
                <span className="font-mono text-nest-text">
                  {amr.path.join(" → ")}
                </span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
