"use client";

import { Wrench } from "@phosphor-icons/react";
import type { AMRState, FleetMaintenanceState } from "@/lib/types";

interface FleetMaintenancePanelProps {
  maintenance: FleetMaintenanceState[];
  paused: boolean;
  amrs: AMRState[];
  offline: boolean;
  loadingId: string | null;
  onBreakdown: (id: string, name: string) => Promise<void>;
}

const statusLabel = {
  normal: "Normal",
  critical: "Crítico",
  broken: "Averiado",
} as const;

export function FleetMaintenancePanel({
  maintenance,
  paused,
  amrs,
  offline,
  loadingId,
  onBreakdown,
}: FleetMaintenancePanelProps) {
  return (
    <section aria-label="Mantenimiento de flota">
      <h3 className="nest-section-title">
        <span>Mantenimiento</span>
        {paused && (
          <span className="rounded-full bg-[#ffe4e6] px-2 py-0.5 text-[0.6rem] font-bold text-nest-red">
            PAUSA
          </span>
        )}
      </h3>
      <p className="mb-2 text-[0.7rem] leading-snug text-nest-muted">
        Desgaste recibido del simulador · {paused ? "flota detenida por mantenimiento" : "flota en operación"}
      </p>
      {maintenance.length === 0 && (
        <p className="rounded-lg border border-dashed border-nest-border px-3 py-2 text-xs text-nest-muted">
          {offline ? "Conecta el backend para ver el mantenimiento de la flota." : "Esperando datos de mantenimiento…"}
        </p>
      )}
      <ul className="space-y-2">
        {maintenance.map((item) => {
          const amr = amrs.find((a) => a.id === item.agv_id);
          const name = amr?.nombre ?? item.agv_id;
          const status = statusLabel[item.status] ?? item.status;
          const critical = item.status === "critical";
          const broken = item.status === "broken";
          const wear = Math.max(0, Math.min(100, Number.isFinite(item.wear_pct) ? item.wear_pct : 0));
          const bar = broken ? "#e4032e" : critical ? "#d97706" : "#059669";
          return (
            <li
              key={item.agv_id}
              className={`rounded-[0.875rem] border p-3 ${
                broken
                  ? "border-nest-red/40 bg-[#fff5f5]"
                  : critical
                    ? "border-amber-700/40 bg-[#fffbeb]"
                    : "border-nest-border bg-nest-panel-raised"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="min-w-0 truncate text-sm font-semibold text-nest-text" title={item.agv_id}>
                  {name}
                </span>
                <span
                  className={`shrink-0 rounded-full px-2 py-0.5 text-[0.65rem] font-bold ${
                    broken
                      ? "bg-[#ffe4e6] text-nest-red"
                      : critical
                        ? "bg-[#fef3c7] text-[#92400e]"
                        : "bg-[#ecfdf5] text-nest-green"
                  }`}
                >
                  {status}
                </span>
              </div>
              <div className="mt-2 flex items-baseline justify-between text-xs text-nest-muted">
                <span>Desgaste</span>
                <span className="font-semibold tabular-nums text-nest-text">{wear.toFixed(0)}%</span>
              </div>
              <div
                className="nest-meter mt-1"
                role="progressbar"
                aria-label={`Desgaste de ${name}`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={wear}
              >
                <span style={{ width: `${wear}%`, background: bar }} />
              </div>
              {item.remaining_seconds > 0 && (
                <p className="mt-1.5 font-mono text-[0.65rem] text-nest-red">
                  Restan {item.remaining_seconds.toFixed(0)} s simulados
                </p>
              )}
              <button
                type="button"
                disabled={offline || loadingId === item.agv_id || broken}
                onClick={() => void onBreakdown(item.agv_id, name)}
                className="nest-btn-danger nest-btn mt-2 w-full text-[0.7rem]"
                title={offline ? "Requiere backend en vivo" : `Simular avería de ${name}`}
              >
                <Wrench size={13} aria-hidden />
                {loadingId === item.agv_id ? "Simulando…" : "Simular avería"}
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
