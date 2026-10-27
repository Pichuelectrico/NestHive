"use client";

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
    <header className="relative z-20 shrink-0 border-b border-black/[0.08] bg-white/90 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4 px-5 py-3 flex-wrap">
        <div className="flex items-center gap-3 min-w-0">
          {/* Logo banner (1159×405, ratio 2.86): caja proporcional, sin barras ni recorte */}
          <div
            className="flex h-8 w-[92px] shrink-0 items-center justify-center overflow-hidden rounded-md border border-nest-accent/40 bg-[#FBFBF8] shadow-nest-glow"
            aria-hidden
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo-nesthive.png" alt="" className="h-full w-full object-contain p-0.5" />
          </div>
          <div className="min-w-0">
            <div className="text-lg font-semibold tracking-tight leading-none">
              <span className="text-nest-text">Nest</span>
              <span className="text-nest-accent">Hive</span>
            </div>
            <div className="nest-label mt-0.5 normal-case tracking-wide text-[0.6rem]">
              Centro de operaciones intralogísticas
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <label className="nest-label" htmlFor="plant-select">
              Planta
            </label>
            <select
              id="plant-select"
              value={selectedPlantId}
              disabled={plantLoading}
              onChange={(e) => onPlantChange(e.target.value)}
              className="nest-select min-w-[140px]"
            >
              {plants.map((p) => (
                <option key={p.id} value={p.id} className="bg-white text-nest-text">
                  {p.nombre}
                </option>
              ))}
              {!plants.length && (
                <option value={selectedPlantId}>{selectedName}</option>
              )}
            </select>
            {plantLoading && (
              <span className="text-xs text-nest-muted animate-pulse">…</span>
            )}
          </div>

          <div className="hidden sm:block h-6 w-px bg-black/[0.1]" aria-hidden />

          {mode === "live" ? (
            <span className="nest-status-live">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              En vivo
            </span>
          ) : mode === "offline" ? (
            <span className="nest-status-offline">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
              Demo local
            </span>
          ) : (
            <span className="nest-btn-ghost nest-btn py-1 text-[0.7rem]">
              Conectando…
            </span>
          )}

          <div className="nest-card flex items-center gap-3 px-3 py-1.5 text-sm">
            <div className="text-right">
              <div className="nest-label leading-none">Sim time</div>
              <div className="font-mono text-sm font-medium text-nest-ink tabular-nums">
                {formatSimTime(simTime)}
              </div>
            </div>
            <div className="h-8 w-px bg-black/[0.1]" aria-hidden />
            <div className="text-right">
              <div className="nest-label leading-none">Flota activa</div>
              <div className="nest-kpi-value text-lg text-nest-text">{amrCount}</div>
            </div>
          </div>

          {onToggleFullscreen && (
            <button
              type="button"
              onClick={onToggleFullscreen}
              className={`nest-btn ${
                fullscreen ? "nest-btn-primary" : "nest-btn-ghost"
              }`}
              title={
                fullscreen
                  ? "Salir de mapa completo (Esc)"
                  : "Abrir mapa en página única"
              }
              aria-pressed={fullscreen}
            >
              {fullscreen ? "⊡ Salir mapa" : "⛶ Mapa"}
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
