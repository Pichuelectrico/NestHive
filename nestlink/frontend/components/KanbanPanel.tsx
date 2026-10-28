"use client";

import { ArrowRight, ArrowsOut } from "@phosphor-icons/react";
import type { Mission } from "@/lib/types";

interface KanbanPanelProps {
  missions: Mission[];
  plantId?: string;
  onExpand: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  pendiente: "Pendiente",
  asignada: "Asignada",
  en_curso: "En curso",
  completada: "Completada",
};

const STATUS_STYLE: Record<string, string> = {
  pendiente: "bg-[#fffbeb] text-[#92400e] border-amber-700/30",
  asignada: "bg-nest-panel text-nest-ink border-nest-border",
  en_curso: "bg-nest-accent/20 text-nest-text border-[#e09c06]/50",
  completada: "bg-[#ecfdf5] text-nest-green border-emerald-700/25",
};

function priorityColor(p: number): string {
  if (p >= 10) return "#e4032e";
  if (p >= 8) return "#c2410c";
  if (p >= 5) return "#d97706";
  return "#059669";
}

const MAX_OPEN = 20;

export function KanbanPanel({ missions, onExpand }: KanbanPanelProps) {
  const sorted = [...missions].sort((a, b) => b.prioridad - a.prioridad);
  const open = sorted.filter((m) => m.estado !== "completada");
  const done = sorted.filter((m) => m.estado === "completada");
  const shown = open.slice(0, MAX_OPEN);

  const counts = {
    pendiente: open.filter((m) => m.estado === "pendiente").length,
    en_curso: open.filter((m) => m.estado === "en_curso" || m.estado === "asignada").length,
  };

  return (
    <section aria-label="Misiones">
      <h3 className="nest-section-title">
        <span>Misiones</span>
        <button
          type="button"
          onClick={onExpand}
          className="nest-btn-ghost nest-btn px-2 py-1 text-[0.65rem] normal-case tracking-normal"
          title="Abrir tablero kanban completo"
        >
          <ArrowsOut size={12} aria-hidden />
          Tablero
        </button>
      </h3>

      <div className="mb-2 grid grid-cols-3 gap-2">
        <div className="nest-tile-soft text-center">
          <p className="text-lg font-semibold tabular-nums text-nest-text">{counts.pendiente}</p>
          <p className="text-[0.65rem] text-nest-muted">Pendientes</p>
        </div>
        <div className="nest-tile-soft text-center">
          <p className="text-lg font-semibold tabular-nums text-nest-text">{counts.en_curso}</p>
          <p className="text-[0.65rem] text-nest-muted">Activas</p>
        </div>
        <div className="nest-tile-soft text-center">
          <p className="text-lg font-semibold tabular-nums text-nest-ink">{done.length}</p>
          <p className="text-[0.65rem] text-nest-muted">Completadas</p>
        </div>
      </div>

      {open.length === 0 && <p className="text-xs text-nest-muted">Sin misiones en cola</p>}
      <ul className="space-y-2">
        {shown.map((m) => (
          <li key={m.id} className="nest-tile-soft">
            <div className="flex items-center justify-between gap-2">
              <span className="flex items-center gap-1.5 text-xs font-semibold text-nest-text">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ background: priorityColor(m.prioridad) }}
                  aria-hidden
                />
                P{m.prioridad}
                <span className="font-mono text-[0.65rem] font-normal text-nest-muted">{m.tipo}</span>
              </span>
              <span
                className={`rounded-full border px-2 py-0.5 text-[0.6rem] font-semibold ${
                  STATUS_STYLE[m.estado] ?? "border-nest-border text-nest-muted"
                }`}
              >
                {STATUS_LABEL[m.estado] ?? m.estado}
              </span>
            </div>
            <p className="mt-1.5 flex items-center gap-1 font-mono text-[0.65rem] text-nest-muted">
              <span className="truncate">{m.origen}</span>
              <ArrowRight size={11} aria-hidden className="shrink-0" />
              <span className="truncate">{m.destino}</span>
            </p>
            {m.amr_asignado && (
              <span className="mt-1.5 inline-block rounded-md border border-nest-border bg-nest-panel px-1.5 py-0.5 font-mono text-[0.6rem] text-nest-ink">
                {m.amr_asignado}
              </span>
            )}
          </li>
        ))}
      </ul>
      {open.length > MAX_OPEN && (
        <p className="mt-2 text-center text-[0.7rem] text-nest-muted">
          +{open.length - MAX_OPEN} más en el tablero
        </p>
      )}
    </section>
  );
}
