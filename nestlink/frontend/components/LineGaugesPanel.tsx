"use client";

import { CollapsibleSidePanel } from "@/components/CollapsibleSidePanel";
import type { LineaState } from "@/lib/types";

interface LineGaugesPanelProps {
  lines: LineaState[];
  collapsed: boolean;
  onToggle: () => void;
}

function levelColor(pct: number): string {
  if (pct < 25) return "#f87171";
  if (pct < 50) return "#fbbf24";
  return "#34d399";
}

export function LineGaugesPanel({
  lines,
  collapsed,
  onToggle,
}: LineGaugesPanelProps) {
  const headerExtra = (
    <span className="flex items-center gap-1.5 min-w-0 normal-case tracking-normal font-medium">
      <span className="text-nest-muted/80 tabular-nums">· {lines.length}</span>
      {lines.length > 0 && (
        <span className="flex items-center gap-0.5" aria-hidden>
          {lines.slice(0, 8).map((line) => (
            <span
              key={line.id}
              className="h-1.5 w-1.5 rounded-full shrink-0"
              style={{ background: levelColor(line.nivel_pct) }}
              title={`${line.nombre}: ${line.nivel_pct.toFixed(0)}%`}
            />
          ))}
          {lines.length > 8 && (
            <span className="text-[0.55rem] text-nest-muted ml-0.5">
              +{lines.length - 8}
            </span>
          )}
        </span>
      )}
    </span>
  );

  return (
    <CollapsibleSidePanel
      title="Insumos por línea"
      collapsed={collapsed}
      onToggle={onToggle}
      onExpand={onToggle}
      headerExtra={headerExtra}
      hideExpand
    >
      {lines.length === 0 && (
        <p className="text-xs text-nest-muted">Sin datos de líneas</p>
      )}
      <div className="space-y-2">
        {lines.map((line) => {
          const low = line.nivel_pct < 25;
          const color = levelColor(line.nivel_pct);
          return (
            <div key={line.id} className="nest-card px-3 py-2.5">
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="min-w-0">
                  <div className="text-sm font-medium text-nest-text truncate">
                    {line.nombre}
                  </div>
                  <div className="text-[0.65rem] text-nest-muted truncate">
                    {line.material}
                  </div>
                </div>
                <span
                  className={`font-mono text-sm font-semibold tabular-nums shrink-0 ${
                    low ? "text-nest-accent" : "text-nest-text"
                  }`}
                >
                  {line.nivel_pct.toFixed(0)}%
                </span>
              </div>
              <div className="h-1.5 rounded-full bg-black/10 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${line.nivel_pct}%`,
                    background: `linear-gradient(90deg, ${color}cc, ${color})`,
                    boxShadow: low ? `0 0 8px ${color}66` : undefined,
                  }}
                />
              </div>
              {low && (
                <div className="mt-1.5 text-[0.65rem] font-medium text-nest-accent">
                  Stock crítico
                </div>
              )}
            </div>
          );
        })}
      </div>
    </CollapsibleSidePanel>
  );
}
