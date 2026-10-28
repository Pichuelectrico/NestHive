"use client";

import { useToast } from "@/hooks/useToast";

export function ToastStack() {
  const { toasts, removeToast } = useToast();

  if (!toasts.length) return null;

  return (
    <div className="fixed bottom-5 left-5 z-50 flex flex-col gap-2 max-w-sm pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          role="status"
          className={`nest-toast ${
            t.type === "error"
              ? "nest-toast-error"
              : t.type === "success"
                ? "nest-toast-success"
                : ""
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <span className="leading-snug">{t.message}</span>
            <button
              type="button"
              onClick={() => removeToast(t.id)}
              className="shrink-0 rounded-md p-0.5 text-nest-muted hover:bg-nest-bg hover:text-nest-text text-xs"
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
