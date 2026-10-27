"use client";

interface CollapsibleSidePanelProps {
  title: string;
  collapsed: boolean;
  onToggle: () => void;
  onExpand: () => void;
  children: React.ReactNode;
  /** Extra content in the header (e.g. status dots when collapsed) */
  headerExtra?: React.ReactNode;
  /** Hide the Expandir button (use when onExpand === onToggle) */
  hideExpand?: boolean;
}

export function CollapsibleSidePanel({
  title,
  collapsed,
  onToggle,
  onExpand,
  children,
  headerExtra,
  hideExpand,
}: CollapsibleSidePanelProps) {
  return (
    <aside
      className={`nest-panel flex flex-col min-h-0 overflow-hidden transition-all duration-300 ${
        collapsed ? "shrink-0" : "flex-1"
      }`}
    >
      <div className="nest-panel-header shrink-0">
        <button
          type="button"
          onClick={onToggle}
          className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.1em] text-nest-muted hover:text-nest-text flex-1 min-w-0 transition-colors"
        >
          <span
            className="flex h-5 w-5 items-center justify-center rounded-md border border-black/[0.1] bg-black/[0.02] text-[0.55rem] transition-transform duration-200"
            style={{ transform: collapsed ? "rotate(-90deg)" : "rotate(0deg)" }}
          >
            ▾
          </span>
          <span className="truncate">{title}</span>
          {headerExtra}
        </button>
        {!hideExpand && (
          <button
            type="button"
            onClick={onExpand}
            className="nest-btn-ghost nest-btn px-2 py-1 text-[0.65rem]"
            title="Expandir vista detallada"
          >
            Expandir
          </button>
        )}
      </div>
      {!collapsed && (
        <div className="flex-1 min-h-0 overflow-y-auto p-3">{children}</div>
      )}
    </aside>
  );
}
