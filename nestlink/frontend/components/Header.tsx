"use client";

import { ArrowsIn, ArrowsOut, Clock, Factory, Robot } from "@phosphor-icons/react";
import type { ConnectionMode, PlantInfo } from "@/lib/types";

interface HeaderProps {
  simTime?: number;
  amrCount: number;
  mode: ConnectionMode;
  plants: PlantInfo[];
  selectedPlantId: string;
  onPlantChange: (plantId: string) => void;
  plantLoading?: boolean;
  fullscreen?: boolean;
  onToggleFullscreen?: () => void;
}

function formatSimTime(seconds: number): string {
  const h = Math.floor(seconds / 3600) % 24;
  const m = Math.floor((seconds % 3600) / 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function Header({
  simTime = 14 * 60 + 23,
  amrCount,
  mode,
  plants,
  selectedPlantId,
  onPlantChange,
  plantLoading,
  fullscreen,
  onToggleFullscreen,
}: HeaderProps) {
  const selectedName =
    plants.find((p) => p.id === selectedPlantId)?.nombre ?? selectedPlantId;

  return (
    <header className="relative z-20 shrink-0 border-b border-nest-border bg-nest-panel">
      <div className="h-0.5 bg-nest-accent" aria-hidden />
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2">
        <div className="flex min-w-0 items-center gap-3">
          {/* Logo banner (1159×405, ratio 2.86): caja proporcional, sin barras ni recorte */}
          <div
            className="flex h-8 w-[92px] shrink-0 items-center justify-center overflow-hidden rounded-lg border border-nest-border bg-nest-bg"
            aria-hidden
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo-nesthive.png" alt="" className="h-full w-full object-contain p-0.5" />
          </div>
          <div className="hidden h-7 w-px bg-nest-border sm:block" aria-hidden />
          <div className="min-w-0">
            <h1 className="nest-wordmark">
              <span className="text-nest-text">Nest</span>
              <span className="text-nest-ink">Hive</span>
            </h1>
            <p className="mt-0.5 hidden text-[0.65rem] text-nest-muted sm:block">
              Centro de operaciones intralogísticas
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <label
            htmlFor="plant-select"
            className="flex items-center gap-2 rounded-lg border border-nest-border bg-nest-bg px-2.5 py-1"
          >
            <Factory size={16} weight="duotone" aria-hidden className="text-nest-muted" />
            <span className="sr-only">Planta</span>
            <select
              id="plant-select"
              value={selectedPlantId}
              disabled={plantLoading}
              onChange={(e) => onPlantChange(e.target.value)}
              className="cursor-pointer bg-transparent text-sm font-medium text-nest-text focus-visible:outline-none"
            >
              {plants.map((p) => (
                <option key={p.id} value={p.id} className="bg-nest-panel text-nest-text">
                  {p.nombre}
                </option>
              ))}
              {!plants.length && <option value={selectedPlantId}>{selectedName}</option>}
            </select>
            {plantLoading && <span className="text-xs text-nest-muted animate-pulse">…</span>}
          </label>

          {mode === "live" ? (
            <span className="nest-status-live">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-600" />
              En vivo
            </span>
          ) : mode === "offline" ? (
            <span className="nest-status-offline">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-600" />
              Demo local
            </span>
          ) : (
            <span className="nest-chip">Conectando…</span>
          )}

          <div className="flex items-center gap-3 rounded-lg border border-nest-border bg-nest-bg px-3 py-1">
            <span className="flex items-center gap-1.5" title="Hora simulada">
              <Clock size={15} weight="duotone" aria-hidden className="text-nest-muted" />
              <span className="sr-only">Hora simulada</span>
              <span className="font-mono text-sm font-medium tabular-nums text-nest-text">
                {formatSimTime(simTime)}
              </span>
            </span>
            <span className="h-4 w-px bg-nest-border" aria-hidden />
            <span className="flex items-center gap-1.5" title="Flota activa">
              <Robot size={15} weight="duotone" aria-hidden className="text-nest-muted" />
              <span className="sr-only">Flota activa</span>
              <span className="text-sm font-semibold tabular-nums text-nest-text">{amrCount}</span>
            </span>
          </div>

          {onToggleFullscreen && (
            <button
              type="button"
              onClick={onToggleFullscreen}
              className="nest-icon-btn"
              aria-pressed={fullscreen}
              aria-label={fullscreen ? "Salir de mapa completo" : "Abrir mapa completo"}
              title={fullscreen ? "Salir de mapa completo (Esc)" : "Abrir mapa completo"}
            >
              {fullscreen ? <ArrowsIn size={16} aria-hidden /> : <ArrowsOut size={16} aria-hidden />}
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
