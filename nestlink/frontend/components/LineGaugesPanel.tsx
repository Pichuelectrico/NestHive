"use client";

import type { LineaState } from "@/lib/types";

interface LineGaugesPanelProps {
  lines: LineaState[];
}

function levelColor(pct: number): string {
  if (pct < 25) return "#e4032e";
  if (pct < 50) return "#d97706";
  return "#059669";
}

export function LineGaugesPanel({ lines }: LineGaugesPanelProps) {
  return (
    <section aria-label="Insumos por línea">
      <h3 className="nest-section-title">
        <span>Insumos por línea</span>
        <span className="nest-chip tabular-nums">{lines.length}</span>
      </h3>
      {lines.length === 0 && <p className="text-xs text-nest-muted">Sin datos de líneas</p>}
      <ul className="space-y-2">
        {lines.map((line) => {
          const low = line.nivel_pct < 25;
          const color = levelColor(line.nivel_pct);
          return (
            <li key={line.id} className="nest-tile-soft">
              <div className="flex items-baseline justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-nest-text">{line.nombre}</p>
                  <p className="truncate text-[0.7rem] text-nest-muted">{line.material}</p>
                </div>
                <span
                  className={`shrink-0 text-sm font-semibold tabular-nums ${low ? "text-nest-red" : "text-nest-text"}`}
                >
                  {line.nivel_pct.toFixed(0)}%
                </span>
              </div>
              <div
                className="nest-meter mt-2"
                role="progressbar"
                aria-label={`Nivel de insumos ${line.nombre}`}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-valuenow={Math.round(line.nivel_pct)}
              >
                <span style={{ width: `${Math.max(0, Math.min(100, line.nivel_pct))}%`, background: color }} />
              </div>
              {low && <p className="mt-1.5 text-[0.7rem] font-semibold text-nest-red">Stock crítico</p>}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
