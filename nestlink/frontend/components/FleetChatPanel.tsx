"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  askChat,
  FALLBACK_CHAT_ASKS,
  fetchChatAsks,
  fetchHourlyReport,
  parseHourlyReportEvent,
  type ChatAskItem,
  type ChatAskResponse,
  type HourlyReport,
} from "@/lib/api";
import { IS_STATIC_PAGES, WS_URL } from "@/lib/config";

function pickDataHighlights(data: Record<string, unknown>): string[] {
  const out: string[] = [];
  if (data.counts && typeof data.counts === "object") {
    const c = data.counts as Record<string, number>;
    out.push(
      Object.entries(c)
        .map(([k, v]) => `${k}: ${v}`)
        .join(" · ")
    );
  }
  if (Array.isArray(data.active)) {
    out.push(`En curso: ${data.active.length}`);
  }
  if (Array.isArray(data.pending)) {
    out.push(`Pendientes: ${data.pending.length}`);
  }
  if (Array.isArray(data.fleet)) {
    out.push(`Flota: ${data.fleet.length} AMR`);
  }
  if (data.kpis && typeof data.kpis === "object") {
    const k = data.kpis as Record<string, unknown>;
    if (typeof k.viajes_completados === "number") {
      out.push(`Viajes: ${k.viajes_completados}`);
    }
    if (typeof k.km_evitados === "number") {
      out.push(`km evit.: ${k.km_evitados}`);
    }
  }
  if (typeof data.rule === "string") out.push(data.rule);
  if (Array.isArray(data.notices)) {
    out.push(`Avisos: ${data.notices.length}`);
  }
  return out.slice(0, 3);
}

function formatReportLine(r: HourlyReport | null): string {
  if (!r) return "Sin reporte aún";
  if (r.status === "pending") return "Reporte horario: pendiente (ventana en curso)";
  const hour = typeof r.sim_hour === "number" ? `h${r.sim_hour}` : "—";
  const mov = r.movements ?? r.delta?.viajes_completados ?? "—";
  const inc = r.incidents ?? "—";
  const km = r.delta?.km_evitados ?? "—";
  return `Reporte ${hour}: ${mov} mov. · ${inc} incid. · Δkm ${km}`;
}

export function FleetChatPanel() {
  const [asks, setAsks] = useState<ChatAskItem[]>(FALLBACK_CHAT_ASKS);
  const [motorOk, setMotorOk] = useState(false);
  const [loadingAsks, setLoadingAsks] = useState(true);
  const [query, setQuery] = useState("");
  const [asking, setAsking] = useState(false);
  const [reply, setReply] = useState<ChatAskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<HourlyReport | null>(null);

  const highlights = useMemo(
    () => (reply ? pickDataHighlights(reply.data) : []),
    [reply]
  );

  const refreshAsks = useCallback(async () => {
    setLoadingAsks(true);
    const list = await fetchChatAsks();
    if (list && list.length) {
      setAsks(list);
      setMotorOk(true);
      setError(null);
    } else {
      setAsks(FALLBACK_CHAT_ASKS);
      setMotorOk(false);
    }
    setLoadingAsks(false);
  }, []);

  const refreshReport = useCallback(async () => {
    const r = await fetchHourlyReport();
    if (r) setReport(r);
  }, []);

  useEffect(() => {
    void refreshAsks();
    void refreshReport();
  }, [refreshAsks, refreshReport]);

  // Polling reporte horario cada 30 s
  useEffect(() => {
    const id = setInterval(() => {
      void refreshReport();
    }, 30_000);
    return () => clearInterval(id);
  }, [refreshReport]);

  // WebSocket: hourly_report_ready (conexión ligera aparte del snapshot)
  useEffect(() => {
    if (IS_STATIC_PAGES) return;
    let ws: WebSocket | null = null;
    let closed = false;
    try {
      ws = new WebSocket(WS_URL);
      ws.onmessage = (ev) => {
        try {
          const raw = JSON.parse(ev.data);
          const hr = parseHourlyReportEvent(raw);
          if (hr) setReport(hr);
        } catch {
          // trama no-JSON o snapshot — ignorar
        }
      };
    } catch {
      // sin WS — el poll cubre
    }
    return () => {
      closed = true;
      if (ws && ws.readyState <= 1) ws.close();
      void closed;
    };
  }, []);

  const runAsk = async (q: string) => {
    const text = q.trim();
    if (!text || asking) return;
    setAsking(true);
    setError(null);
    setQuery(text);
    const res = await askChat(text);
    if (res) {
      setReply(res);
      setMotorOk(true);
    } else {
      setReply(null);
      setMotorOk(false);
      setError("Motor no disponible — el asistente no pudo consultar el gemelo.");
    }
    setAsking(false);
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    void runAsk(query);
  };

  return (
    <div className="nest-panel shrink-0 px-2 py-1.5 space-y-1.5">
      <div className="flex items-center justify-between gap-2 px-1">
        <div className="nest-label">💬 Asistente de flota</div>
        <span
          className={`text-[0.6rem] font-medium ${
            motorOk ? "text-emerald-700" : "text-amber-700"
          }`}
        >
          {loadingAsks
            ? "conectando…"
            : motorOk
              ? "en línea"
              : "motor no disponible"}
        </span>
      </div>

      {!motorOk && !loadingAsks && (
        <p className="px-1 text-[0.65rem] text-amber-800/90 leading-snug">
          Motor no disponible — las preguntas se muestran, pero el gemelo aún no
          responde. El resto del dashboard sigue operativo.
        </p>
      )}

      <div className="flex flex-wrap gap-1 max-h-[4.5rem] overflow-y-auto px-0.5">
        {asks.map((a) => (
          <button
            key={a.id}
            type="button"
            disabled={asking}
            onClick={() => void runAsk(a.question)}
            title={a.question}
            className="nest-btn nest-btn-ghost max-w-full truncate text-[0.6rem] py-0.5 px-1.5"
          >
            {a.question.length > 42 ? `${a.question.slice(0, 40)}…` : a.question}
          </button>
        ))}
      </div>

      <form onSubmit={onSubmit} className="flex gap-1.5 items-center">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Pregunta libre (keywords)…"
          className="nest-select flex-1 min-w-0 text-xs py-1"
          disabled={asking}
          aria-label="Pregunta al asistente de flota"
        />
        <button
          type="submit"
          disabled={asking || !query.trim()}
          className="nest-btn nest-btn-primary text-xs py-1 px-2 shrink-0"
        >
          {asking ? "…" : "Preguntar"}
        </button>
      </form>

      {(reply || error) && (
        <div className="nest-card px-2 py-1.5 space-y-1">
          {error && (
            <p className="text-[0.7rem] text-amber-800 leading-snug">{error}</p>
          )}
          {reply && (
            <>
              <p className="text-[0.75rem] text-nest-text leading-snug">
                {reply.answer}
              </p>
              {highlights.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {highlights.map((h) => (
                    <span
                      key={h}
                      className="rounded bg-nest-accent/10 px-1.5 py-0.5 text-[0.6rem] text-nest-ink font-mono"
                    >
                      {h}
                    </span>
                  ))}
                </div>
              )}
              <p className="text-[0.55rem] text-nest-muted font-mono">
                {typeof reply.ts === "string" ? reply.ts : `ts ${reply.ts}`}
              </p>
            </>
          )}
        </div>
      )}

      <div className="border-t border-black/[0.06] pt-1 px-1">
        <p className="text-[0.65rem] text-nest-muted leading-snug">
          <span className="font-medium text-nest-text">Reporte horario · </span>
          {formatReportLine(report)}
        </p>
      </div>
    </div>
  );
}
