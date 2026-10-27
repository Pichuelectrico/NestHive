"use client";

import { CollapsibleSidePanel } from "@/components/CollapsibleSidePanel";
import { priorityClass, priorityEmoji } from "@/lib/amrColors";
import type { Mission } from "@/lib/types";

interface KanbanPanelProps {
  missions: Mission[];
  collapsed: boolean;
  onToggle: () => void;
  onExpand: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  pendiente: "Pendiente",
  asignada: "Asignada",
  en_curso: "En curso",
  completada: "Completada",
};

const STATUS_STYLE: Record<string, string> = {
  pendiente: "text-amber-700/90",
  asignada: "text-nest-accent",
  en_curso: "text-purple-700",
  completada: "text-emerald-700",
};

export function KanbanPanel({
  missions,
  collapsed,
  onToggle,
  onExpand,
}: KanbanPanelProps) {
  const sorted = [...missions].sort((a, b) => b.prioridad - a.prioridad);

  return (
    <CollapsibleSidePanel
      title="Kanban de misiones"
      collapsed={collapsed}
      onToggle={onToggle}
      onExpand={onExpand}
    >
      <div className="space-y-2">
        {sorted.length === 0 && (
          <p className="text-xs text-nest-muted">Sin misiones en cola</p>
        )}
        {sorted.map((m) => (
          <div
            key={m.id}
            className={`nest-card border-l-2 p-2.5 text-xs ${priorityClass(m.prioridad)}`}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="font-medium text-nest-text">
                {priorityEmoji(m.prioridad)} P{m.prioridad}
              </span>
              <span className="font-mono text-[0.65rem] text-nest-muted">
                {m.tipo}
              </span>
            </div>
            <div className="mt-1 font-mono text-[0.65rem] text-nest-muted">
              {m.origen} → {m.destino}
            </div>
            <div
              className={`mt-1.5 text-[0.65rem] font-medium capitalize ${
                STATUS_STYLE[m.estado] ?? "text-nest-muted"
              }`}
            >
              {STATUS_LABEL[m.estado] ?? m.estado}
            </div>
            {m.amr_asignado && (
              <span className="mt-1.5 inline-block rounded-md border border-black/[0.08] bg-black/[0.03] px-1.5 py-0.5 font-mono text-[0.6rem] text-nest-accent">
                {m.amr_asignado}
              </span>
            )}
          </div>
        ))}
      </div>
    </CollapsibleSidePanel>
  );
}
