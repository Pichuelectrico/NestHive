"use client";
import type { Notice } from "@/lib/types";

interface NoticeBannerProps {
  notices: (string | Notice)[];
}

function label(n: string | Notice): string {
  if (typeof n === "string") return n;
  return n.mensaje ?? n.tipo ?? "Aviso";
}

function noticeKey(n: string | Notice, i: number): string {
  const base = typeof n === "string" ? n : `${n.tipo}-${n.sim_time ?? "?"}`;
  return `${base}-${i}`;
}

export function NoticeBanner({ notices }: NoticeBannerProps) {
  if (!notices?.length) return null;

  return (
    <div className="flex flex-wrap gap-2 border-b border-black/[0.06] bg-amber-500/[0.04] px-4 py-2">
      {notices.map((n, i) => (
        <span
          key={noticeKey(n, i)}
          className="inline-flex items-center gap-2 rounded-lg border border-amber-500/25 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-100/90"
        >
          <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
          {label(n)}
        </span>
      ))}
    </div>
  );
}
