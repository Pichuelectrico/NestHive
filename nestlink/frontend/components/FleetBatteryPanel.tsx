"use client";

import { ArrowsOut, BatteryCharging, BatteryWarning } from "@phosphor-icons/react";
import { AMR_STATE_COLORS } from "@/lib/amrColors";
import type { AMRState } from "@/lib/types";

interface FleetBatteryPanelProps {
  amrs: AMRState[];
  plantId?: string;
  onLowBattery: (amrId: string, nombre: string) => Promise<void>;
  loadingId: string | null;
  onExpand: () => void;
}

function batteryBarColor(pct: number): string {
  if (pct <= 25) return "#e4032e";
  if (pct <= 50) return "#d97706";
  return "#059669";
}

function estadoLabel(estado: string): string {
  return estado.replace(/_/g, " ").toLowerCase();
}

export function FleetBatteryPanel({ amrs, onLowBattery, loadingId, onExpand }: FleetBatteryPanelProps) {
  return (
    <section aria-label="Flota y batería">
      <h3 className="nest-section-title">
        <span>Flota · batería</span>
        <button
          type="button"
          onClick={onExpand}
          className="nest-btn-ghost nest-btn px-2 py-1 text-[0.65rem] normal-case tracking-normal"
          title="Abrir vista detallada de la flota"
        >
          <ArrowsOut size={12} aria-hidden />
          Detalle
        </button>
      </h3>
      {amrs.length === 0 && <p className="text-xs text-nest-muted">Sin AMRs en snapshot</p>}
      <ul className="space-y-2">
        {amrs.map((amr) => {
          const ring = AMR_STATE_COLORS[amr.estado] ?? "#8b9aad";
          const pct = Math.max(0, Math.min(100, amr.bateria));
          const color = batteryBarColor(amr.bateria);
          const charging = amr.estado === "CHARGING";
          return (
            <li key={amr.id} className="nest-tile-soft">
              <div className="flex items-center justify-between gap-2">
                <div className="flex min-w-0 items-center gap-2">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ background: ring }}
                    aria-hidden
                  />
                  <span className="truncate text-sm font-semibold text-nest-text">{amr.nombre}</span>
                </div>
                <span className="flex shrink-0 items-center gap-1 text-sm font-semibold tabular-nums text-nest-text">
                  {charging && <BatteryCharging size={14} weight="fill" aria-hidden className="text-nest-ink" />}
                  {amr.bateria}%
                </span>
              </div>
              <div className="mt-1.5 flex items-center justify-between gap-2">
                <span className="nest-chip capitalize">{estadoLabel(amr.estado)}</span>
                <button
                  type="button"
                  disabled={loadingId === amr.id}
                  onClick={() => onLowBattery(amr.id, amr.nombre)}
                  className="nest-btn-ghost nest-btn px-2 py-0.5 text-[0.65rem]"
                  title="Simular batería al 15%"
                  aria-label={`Simular batería al 15% en ${amr.nombre}`}
                >
                  <BatteryWarning size={13} aria-hidden />
                  15%
                </button>
              </div>
              <div
                className="nest-meter mt-2"
                role="progressbar"
                aria-label={`Batería de ${amr.nombre}`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={pct}
              >
                <span style={{ width: `${pct}%`, background: color }} />
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
