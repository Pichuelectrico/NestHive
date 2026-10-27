"use client";

import type { KPIsState } from "@/lib/types";

interface KpiMiniPanelProps {
  kpis: KPIsState;
}

export function KpiMiniPanel({ kpis }: KpiMiniPanelProps) {
  const items = [
    {
      label: "Viajes",
      value: String(kpis.viajes_completados),
      accent: "text-nest-accent",
    },
    {
      label: "Vacíos evit.",
      value: String(kpis.viajes_vacios_evitados),
      accent: "text-[#9f1239]",
    },
    {
      label: "Paradas",
      value: String(kpis.paradas_evitadas),
      accent: "text-amber-700",
    },
    {
      label: "T. medio",
      value: `${kpis.tiempo_medio_entrega_min.toFixed(1)}m`,
      accent: "text-nest-text",
    },
    {
      label: "OUT (prom.)",
      value: `${kpis.tiempo_medio_en_out_min.toFixed(1)}m`,
      accent: "text-violet-700",
    },
    {
      label: "km evit.",
      value: kpis.km_evitados.toFixed(1),
      accent: "text-[#c40026]",
    },
    {
      label: "ROI km",
      value: `−${kpis.roi_km_pct}%`,
      accent: "text-emerald-700",
      highlight: true,
    },
  ];

  return (
    <div className="nest-panel shrink-0 p-2">
      <div className="nest-label mb-1.5 px-1">KPIs</div>
      <div className="grid grid-cols-3 gap-1.5">
        {items.map((item) => (
          <div
            key={item.label}
            className={`nest-card px-1.5 py-1.5 text-center ${
              item.highlight ? "border-emerald-600/25 bg-emerald-50" : ""
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
