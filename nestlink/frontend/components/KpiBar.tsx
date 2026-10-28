"use client";

import type { KPIsState } from "@/lib/types";

interface KpiBarProps {
  kpis: KPIsState;
}

export function KpiBar({ kpis }: KpiBarProps) {
  const items = [
    {
      label: "Viajes completados",
      value: kpis.viajes_completados,
      accent: "text-nest-ink",
    },
    {
      label: "Vacíos evitados",
      value: kpis.viajes_vacios_evitados,
      accent: "text-nest-text",
    },
    {
      label: "Paradas evitadas",
      value: kpis.paradas_evitadas,
      accent: "text-nest-text",
    },
    {
      label: "Tiempo medio",
      value: `${kpis.tiempo_medio_entrega_min.toFixed(1)} min`,
      accent: "text-nest-text",
    },
    {
      label: "En OUT (prom.)",
      value: `${kpis.tiempo_medio_en_out_min.toFixed(1)} min`,
      accent: "text-nest-text",
    },
    {
      label: "ROI distancia",
      value: `−${kpis.roi_km_pct}% km`,
      accent: "text-nest-ink",
      highlight: true,
    },
  ];

  return (
    <div className="nest-panel flex flex-wrap items-stretch gap-2 px-3 py-2.5">
      {items.map((item) => (
        <div
          key={item.label}
          className={`nest-card flex-1 min-w-[100px] px-4 py-2.5 text-center ${
            item.highlight ? "border-nest-accent/50 bg-nest-accent/15" : ""
          }`}
        >
          <div className={`nest-kpi-value ${item.accent}`}>{item.value}</div>
          <div className="nest-label mt-1 normal-case tracking-wide">
            {item.label}
          </div>
        </div>
      ))}
    </div>
  );
}
