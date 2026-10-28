"use client";

import { Gauge, Package, Path, Timer, Truck, Warning } from "@phosphor-icons/react";
import type { ReactNode } from "react";
import type { KPIsState } from "@/lib/types";

interface KpiMiniPanelProps {
  kpis: KPIsState;
  plantId?: string;
}

function Stat({
  icon,
  label,
  value,
  tone = "text-nest-text",
}: {
  icon: ReactNode;
  label: string;
  value: string;
  tone?: string;
}) {
  return (
    <div className="nest-tile">
      <div className="flex items-center gap-1.5 text-nest-muted">
        {icon}
        <span className="truncate text-[0.7rem] font-medium">{label}</span>
      </div>
      <div className={`mt-1.5 text-xl font-semibold tabular-nums leading-none ${tone}`}>{value}</div>
    </div>
  );
}

export function KpiMiniPanel({ kpis }: KpiMiniPanelProps) {
  const assists = kpis.amr_emergency_assists ?? 0;

  return (
    <section aria-label="Indicadores clave" className="space-y-2">
      <div className="nest-tile-hero">
        <div className="relative z-10 flex items-start justify-between gap-3">
          <div>
            <p className="text-[0.65rem] font-semibold uppercase tracking-[0.12em] text-[#e9d7b4]">
              Ahorro de distancia
            </p>
            <p className="mt-1 text-3xl font-semibold leading-none tabular-nums text-nest-accent">
              −{kpis.roi_km_pct}%
            </p>
            <p className="mt-1.5 text-xs text-[#e9d7b4]">
              <span className="font-mono tabular-nums text-[#fbf3e4]">{kpis.km_evitados.toFixed(1)}</span> km
              evitados
            </p>
          </div>
          <Path size={28} weight="duotone" aria-hidden className="text-nest-accent" />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Stat
          icon={<Truck size={15} weight="duotone" aria-hidden />}
          label="Viajes"
          value={String(kpis.viajes_completados)}
        />
        <Stat
          icon={<Package size={15} weight="duotone" aria-hidden />}
          label="Vacíos evitados"
          value={String(kpis.viajes_vacios_evitados)}
        />
        <Stat
          icon={<Timer size={15} weight="duotone" aria-hidden />}
          label="Tiempo medio"
          value={`${kpis.tiempo_medio_entrega_min.toFixed(1)} min`}
        />
        <Stat
          icon={<Gauge size={15} weight="duotone" aria-hidden />}
          label="Espera OUT"
          value={`${kpis.tiempo_medio_en_out_min.toFixed(1)} min`}
        />
        <Stat
          icon={<Warning size={15} weight="duotone" aria-hidden />}
          label="Paradas evitadas"
          value={String(kpis.paradas_evitadas)}
        />
        <Stat
          icon={<Warning size={15} weight="duotone" aria-hidden />}
          label="Asistencias AMR"
          value={String(assists)}
          tone={assists > 0 ? "text-nest-red" : "text-nest-text"}
        />
      </div>
    </section>
  );
}
