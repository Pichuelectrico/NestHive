"use client";

import type { AMRState, FleetMaintenanceState } from "@/lib/types";
import { CollapsibleSidePanel } from "@/components/CollapsibleSidePanel";

interface FleetMaintenancePanelProps {
  maintenance: FleetMaintenanceState[];
  paused: boolean;
  amrs: AMRState[];
  offline: boolean;
  loadingId: string | null;
  collapsed: boolean;
  onToggle: () => void;
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
  collapsed,
  onToggle,
  onBreakdown,
}: FleetMaintenancePanelProps) {
  return (
    <CollapsibleSidePanel
      title="Prevención de mantenimiento de flota"
      collapsed={collapsed}
      onToggle={onToggle}
      onExpand={onToggle}
      hideExpand
      headerExtra={paused ? <span className="rounded bg-red-100 px-1.5 py-0.5 text-[0.6rem] font-bold text-red-800">PAUSA</span> : undefined}
    >
      <div className="space-y-2">
        <p className="text-[0.7rem] leading-snug text-nest-muted">
          Desgaste recibido del simulador · {paused ? "flota detenida por mantenimiento" : "flota en operación"}
        </p>
        {maintenance.length === 0 && (
          <p className="rounded-lg border border-dashed border-[#5B3918]/25 px-3 py-2 text-xs text-nest-muted">
            {offline ? "Conecta el backend para ver el mantenimiento de la flota." : "Esperando datos de mantenimiento…"}
          </p>
        )}
        {maintenance.map((item) => {
          const amr = amrs.find((a) => a.id === item.agv_id);
          const name = amr?.nombre ?? item.agv_id;
          const status = statusLabel[item.status] ?? item.status;
          const critical = item.status === "critical";
          const broken = item.status === "broken";
          const wear = Math.max(0, Math.min(100, Number.isFinite(item.wear_pct) ? item.wear_pct : 0));
          return (
            <div key={item.agv_id} className={`rounded-lg border p-2.5 text-xs ${broken ? "border-red-500/45 bg-red-50" : critical ? "border-amber-600/45 bg-amber-50" : "border-[#5B3918]/15 bg-white/75"}`}>
              <div className="flex items-center justify-between gap-2">
                <span className="min-w-0 truncate font-semibold text-nest-text" title={item.agv_id}>{name}</span>
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-[0.65rem] font-bold ${broken ? "bg-red-100 text-red-800" : critical ? "bg-amber-200 text-amber-950" : "bg-emerald-100 text-emerald-800"}`}>{status}</span>
              </div>
              <div className="mt-2 flex items-baseline justify-between text-nest-muted">
                <span>Desgaste</span>
                <span className="font-mono font-bold tabular-nums text-nest-text">{wear.toFixed(0)}%</span>
              </div>
              <div className="mt-1 h-2 overflow-hidden rounded-full bg-[#5B3918]/10" role="progressbar" aria-label={`Desgaste de ${name}`} aria-valuemin={0} aria-valuemax={100} aria-valuenow={wear}>
                <div className={`h-full rounded-full transition-[width] duration-300 ${broken ? "bg-red-600" : critical ? "bg-amber-600" : "bg-emerald-600"}`} style={{ width: `${wear}%` }} />
              </div>
              {item.remaining_seconds > 0 && <p className="mt-1.5 font-mono text-[0.65rem] text-red-800">Restan {item.remaining_seconds.toFixed(0)} s simulados</p>}
              <button
                type="button"
                disabled={offline || loadingId === item.agv_id || broken}
                onClick={() => void onBreakdown(item.agv_id, name)}
                className="nest-btn-danger mt-2 w-full text-[0.7rem]"
                title={offline ? "Requiere backend en vivo" : `Simular avería de ${name}`}
              >
                {loadingId === item.agv_id ? "Simulando…" : "Simular avería"}
              </button>
            </div>
          );
        })}
      </div>
    </CollapsibleSidePanel>
  );
}
