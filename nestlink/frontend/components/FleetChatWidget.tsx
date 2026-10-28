"use client";

import { Siren, X } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
import { FleetChatPanel } from "@/components/FleetChatPanel";
import { BASE_PATH } from "@/lib/config";

const PANEL_ID = "fleet-chat-widget-panel";
const AVATAR_SRC = `${BASE_PATH}/nestor.jpeg`;

/**
 * Asistente de flota como chat flotante: botón Néstor fijo abajo-derecha.
 * Cerrado por defecto (sin persistencia) para que la demo arranque con el mapa limpio.
 * El panel queda MONTADO aunque esté cerrado (`hidden` → display:none, no captura clicks)
 * para conservar el WS de reporte horario, el polling y la última respuesta.
 */
export function FleetChatWidget({ breakdownAlert }: { breakdownAlert?: { key: string; message: string } | null }) {
  const [open, setOpen] = useState(false);
  const [activeAlert, setActiveAlert] = useState<string | null>(null);
  const lastAlertKey = useRef<string | null>(null);

  useEffect(() => {
    if (!breakdownAlert) {
      lastAlertKey.current = null;
      return;
    }
    if (breakdownAlert.key === lastAlertKey.current) return;
    lastAlertKey.current = breakdownAlert.key;
    setActiveAlert(breakdownAlert.message);
    setOpen(true);
  }, [breakdownAlert?.key, breakdownAlert?.message]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  return (
    <>
      <div
        id={PANEL_ID}
        role="dialog"
        aria-label="Néstor · Asistente de flota"
        hidden={!open}
        className="nest-panel fixed bottom-20 right-4 z-40 w-[22rem] max-w-[calc(100vw-2rem)] max-h-[60vh] overflow-y-auto border-t-2 border-t-nest-accent p-1.5 shadow-nest-glow"
      >
        <div className="flex items-center gap-2 px-1 pb-1.5">
          <img
            src={AVATAR_SRC}
            alt=""
            className="h-6 w-[42px] rounded-md object-cover object-center"
          />
          <span className="flex-1 text-xs font-semibold text-nest-text">
            Néstor · Asistente de flota
          </span>
          <button
            type="button"
            onClick={() => setOpen(false)}
            aria-label="Cerrar asistente de flota"
            className="nest-icon-btn !h-6 !w-6"
          >
            <X size={12} aria-hidden />
          </button>
        </div>
        {activeAlert && (
          <div className="mx-1 mb-2 rounded-lg border border-nest-red/35 bg-[#fff5f5] px-3 py-2" role="alert">
            <p className="flex items-center gap-1 text-[0.65rem] font-bold uppercase tracking-wide text-nest-red">
              <Siren size={13} weight="fill" aria-hidden />
              Aviso de mantenimiento
            </p>
            <p className="mt-0.5 text-xs leading-snug text-nest-text">{activeAlert}</p>
          </div>
        )}
        <FleetChatPanel />
      </div>

      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? "Cerrar asistente de flota" : "Abrir asistente de flota"}
        aria-expanded={open}
        aria-controls={PANEL_ID}
        title="Néstor · Asistente de flota"
        className="group fixed bottom-4 right-4 z-40 flex items-center gap-2"
      >
        <span className="block h-12 w-[84px] overflow-hidden rounded-2xl bg-nest-panel ring-2 ring-nest-accent/70 shadow-nest-panel transition-shadow group-hover:ring-nest-accent">
          <img
            src={AVATAR_SRC}
            alt=""
            className="h-full w-full object-cover object-center"
          />
        </span>
        <span className="hidden rounded-full border border-nest-border bg-nest-panel px-2 py-0.5 text-xs font-semibold text-nest-text shadow-nest-panel md:inline">
          {open ? "Cerrar" : "Néstor"}
        </span>
      </button>
    </>
  );
}
