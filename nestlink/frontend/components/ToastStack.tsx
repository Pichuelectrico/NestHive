"use client";

import { CheckCircle, Info, WarningCircle, X } from "@phosphor-icons/react";
import { useToast } from "@/hooks/useToast";

export function ToastStack() {
  const { toasts, removeToast } = useToast();

  if (!toasts.length) return null;

  return (
    <div
      className="pointer-events-none fixed bottom-5 left-5 z-50 flex max-w-sm flex-col gap-2"
      aria-live="polite"
    >
      {toasts.map((t) => {
        const Icon = t.type === "error" ? WarningCircle : t.type === "success" ? CheckCircle : Info;
        return (
          <div
            key={t.id}
            role="status"
            className={`nest-toast ${
              t.type === "error" ? "nest-toast-error" : t.type === "success" ? "nest-toast-success" : ""
            }`}
          >
            <div className="flex items-start gap-2.5">
              <Icon size={18} weight="fill" aria-hidden className="mt-0.5 shrink-0" />
              <span className="flex-1 leading-snug">{t.message}</span>
              <button
                type="button"
                onClick={() => removeToast(t.id)}
                className="shrink-0 rounded-md p-0.5 text-nest-muted transition-colors hover:bg-nest-bg hover:text-nest-text"
                aria-label="Cerrar notificación"
              >
                <X size={14} aria-hidden />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
