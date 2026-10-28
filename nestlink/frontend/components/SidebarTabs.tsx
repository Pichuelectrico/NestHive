"use client";

import { useRef, type KeyboardEvent, type ReactNode } from "react";

export interface SidebarTab {
  id: string;
  label: string;
  icon: ReactNode;
  /** Pequeño contador (ej. misiones activas). */
  badge?: number | string;
}

interface SidebarTabsProps {
  tabs: SidebarTab[];
  active: string;
  onChange: (id: string) => void;
  children: ReactNode;
}

/** Contenedor del sidebar: tabs accesibles (flechas ← →) + cuerpo con scroll. */
export function SidebarTabs({ tabs, active, onChange, children }: SidebarTabsProps) {
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft" && e.key !== "Home" && e.key !== "End") return;
    e.preventDefault();
    const idx = tabs.findIndex((t) => t.id === active);
    let next = idx;
    if (e.key === "ArrowRight") next = (idx + 1) % tabs.length;
    if (e.key === "ArrowLeft") next = (idx - 1 + tabs.length) % tabs.length;
    if (e.key === "Home") next = 0;
    if (e.key === "End") next = tabs.length - 1;
    const id = tabs[next].id;
    onChange(id);
    refs.current[id]?.focus();
  };

  return (
    <aside className="nest-panel flex h-full min-h-0 flex-col overflow-hidden">
      <div className="shrink-0 p-2">
        <div role="tablist" aria-label="Secciones del panel" className="nest-tabs" onKeyDown={onKeyDown}>
          {tabs.map((tab) => {
            const selected = tab.id === active;
            return (
              <button
                key={tab.id}
                ref={(el) => {
                  refs.current[tab.id] = el;
                }}
                id={`sidebar-tab-${tab.id}`}
                role="tab"
                type="button"
                aria-selected={selected}
                aria-controls={`sidebar-panel-${tab.id}`}
                tabIndex={selected ? 0 : -1}
                onClick={() => onChange(tab.id)}
                className="nest-tab relative"
              >
                <span className="relative">
                  {tab.icon}
                  {tab.badge !== undefined && tab.badge !== 0 && (
                    <span className="absolute -right-2.5 -top-1.5 min-w-[1rem] rounded-full bg-nest-text px-1 text-center text-[0.55rem] font-semibold leading-4 text-nest-panel">
                      {tab.badge}
                    </span>
                  )}
                </span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
      <div
        role="tabpanel"
        id={`sidebar-panel-${active}`}
        aria-labelledby={`sidebar-tab-${active}`}
        className="nest-scroll min-h-0 flex-1 space-y-3 overflow-y-auto overflow-x-hidden px-2 pb-3 pt-1"
      >
        {children}
      </div>
    </aside>
  );
}
