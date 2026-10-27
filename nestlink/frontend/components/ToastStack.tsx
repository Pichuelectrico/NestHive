"use client";

import { useToast } from "@/hooks/useToast";

export function ToastStack() {
  const { toasts, removeToast } = useToast();

  if (!toasts.length) return null;

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          role="status"
          className={`pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow-nest-panel backdrop-blur-xl animate-in slide-in-from-right ${
            t.type === "error"
              ? "border-nest-accent/40 bg-red-50 text-[#8b001c]"
              : t.type === "success"
                ? "border-emerald-600/35 bg-emerald-50 text-emerald-900"
                : "border-black/[0.1] bg-white/95 text-nest-text"
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <span className="leading-snug">{t.message}</span>
            <button
              type="button"
              onClick={() => removeToast(t.id)}
              className="shrink-0 rounded-md p-0.5 text-nest-muted hover:bg-black/[0.05] hover:text-nest-text text-xs"
              aria-label="Cerrar"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
