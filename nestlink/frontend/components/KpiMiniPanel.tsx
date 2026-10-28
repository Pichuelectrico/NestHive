"use client";

import type { KPIsState } from "@/lib/types";

interface KpiMiniPanelProps {
  kpis: KPIsState;
  plantId?: string;
}

export function KpiMiniPanel({ kpis, plantId }: KpiMiniPanelProps) {
  const items = [
    {
      label: "Viajes",
      value: String(kpis.viajes_completados),
      accent: "text-nest-ink",
    },
    {
      label: "Vacíos evit.",
      value: String(kpis.viajes_vacios_evitados),
      accent: "text-nest-text",
    },
    {
      label: "Paradas",
      value: String(kpis.paradas_evitadas),
      accent: "text-nest-text",
    },
    {
      label: "T. medio",
      value: `${kpis.tiempo_medio_entrega_min.toFixed(1)}m`,
      accent: "text-nest-text",
    },
    {
      label: "OUT (prom.)",
      value: `${kpis.tiempo_medio_en_out_min.toFixed(1)}m`,
      accent: "text-nest-text",
    },
    {
      label: "km evit.",
      value: kpis.km_evitados.toFixed(1),
      accent: "text-nest-text",
    },
    {
      label: "ROI km",
      value: `−${kpis.roi_km_pct}%`,
      accent: "text-nest-ink",
      highlight: true,
    },
    { label: "Asistencias AMR", value: String(kpis.amr_emergency_assists ?? 0), accent: "text-nest-red" },
  ];

  return (
    <div className="nest-panel shrink-0 p-2">
      <div className="nest-label mb-1.5 px-1">KPIs</div>
      <div className="grid grid-cols-3 gap-1.5">
        {items.map((item) => (
          <div
            key={item.label}
            className={`nest-card px-1.5 py-1.5 text-center ${
              item.highlight ? "border-nest-accent/50 bg-nest-accent/15" : ""
            }`}
          >
            <div
              className={`font-mono text-xs font-semibold tabular-nums leading-tight ${item.accent}`}
            >
              {item.value}
            </div>
            <div className="mt-0.5 text-[0.55rem] leading-tight text-nest-muted truncate">
              {item.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
