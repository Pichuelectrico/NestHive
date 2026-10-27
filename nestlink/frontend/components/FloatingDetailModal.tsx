"use client";

import { useCallback, useRef, useState } from "react";

interface FloatingDetailModalProps {
  title: string;
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export function FloatingDetailModal({
  title,
  open,
  onClose,
  children,
}: FloatingDetailModalProps) {
  const [pos, setPos] = useState({ x: 72, y: 56 });
  const dragRef = useRef<{
    startX: number;
    startY: number;
    origX: number;
    origY: number;
  } | null>(null);

  const onHeaderMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if ((e.target as HTMLElement).closest("button")) return;
      dragRef.current = {
        startX: e.clientX,
        startY: e.clientY,
        origX: pos.x,
        origY: pos.y,
      };
      const onMove = (ev: MouseEvent) => {
        if (!dragRef.current) return;
        setPos({
          x: dragRef.current.origX + ev.clientX - dragRef.current.startX,
          y: dragRef.current.origY + ev.clientY - dragRef.current.startY,
        });
      };
      const onUp = () => {
        dragRef.current = null;
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };
      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    },
    [pos.x, pos.y]
  );

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center p-4 pointer-events-none">
      <div
        className="absolute inset-0 bg-slate-900/30 backdrop-blur-sm pointer-events-auto"
        onClick={onClose}
        aria-hidden
      />
      <div
        className="nest-panel pointer-events-auto relative flex flex-col shadow-2xl resize overflow-hidden min-w-[min(90vw,520px)] min-h-[min(70vh,360px)] w-[min(88vw,900px)] h-[min(75vh,560px)] max-w-[95vw] max-h-[90vh]"
        style={{ left: pos.x, top: pos.y, position: "fixed" }}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div
          className="nest-panel-header cursor-move select-none shrink-0"
          onMouseDown={onHeaderMouseDown}
        >
          <h2 className="text-sm font-semibold text-nest-text">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="nest-btn-ghost nest-btn px-2 py-1"
            aria-label="Cerrar"
          >
            Cerrar
          </button>
        </div>
        <div className="flex-1 overflow-auto p-4 min-h-0">{children}</div>
      </div>
    </div>
  );
}
