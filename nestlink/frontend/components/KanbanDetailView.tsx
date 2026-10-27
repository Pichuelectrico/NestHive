"use client";

import { priorityClass, priorityEmoji } from "@/lib/amrColors";
import type { Mission } from "@/lib/types";

const COLUMNS: Array<{ key: Mission["estado"]; label: string }> = [
  { key: "pendiente", label: "Pendiente" },
  { key: "en_curso", label: "En curso" },
  { key: "asignada", label: "Asignada" },
  { key: "completada", label: "Completada" },
];

interface KanbanDetailViewProps {
  missions: Mission[];
}

export function KanbanDetailView({ missions }: KanbanDetailViewProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 min-h-[200px]">
      {COLUMNS.map((col) => {
        const items = missions
          .filter((m) => m.estado === col.key)
          .sort((a, b) => b.prioridad - a.prioridad);
        return (
          <div
            key={col.key}
            className="nest-panel p-2 min-h-[120px]"
          >
            <h4 className="nest-label mb-2 pb-2 border-b border-black/[0.06]">
              {col.label}
              <span className="ml-1 text-nest-accent">({items.length})</span>
            </h4>
            <div className="space-y-2">
              {items.length === 0 && (
                <p className="text-[0.65rem] text-nest-muted">—</p>
              )}
              {items.map((m) => (
                <div
                  key={m.id}
                  className={`nest-card border-l-2 p-2 text-xs ${priorityClass(m.prioridad)}`}
                >
                  <div className="font-mono text-[0.65rem] text-nest-muted">
                    {m.id}
                  </div>
                  <div className="font-semibold mt-0.5">
                    {priorityEmoji(m.prioridad)} P{m.prioridad} · {m.tipo}
                  </div>
                  <div className="text-nest-muted mt-1">
                    {m.origen} → {m.destino}
                  </div>
                  {m.amr_asignado && (
                    <div className="mt-1 text-[0.65rem]">
                      🤖 {m.amr_asignado}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
