"use client";

/**
 * Panel de tendencias con Recharts.
 * TODO: conectar a GET /api/v1/metrics para histórico real de viajes y ROI.
 */
import { TrendUp } from "@phosphor-icons/react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const DEMO_TREND = [
  { t: "10:00", viajes: 4, roi: 12 },
  { t: "11:00", viajes: 8, roi: 15 },
  { t: "12:00", viajes: 12, roi: 18 },
  { t: "13:00", viajes: 15, roi: 20 },
  { t: "14:00", viajes: 18, roi: 22 },
];

export function TrendsPanel() {
  return (
    <section className="nest-tile" aria-label="Tendencia de viajes">
      <h3 className="nest-section-title">
        <span className="flex items-center gap-1.5">
          <TrendUp size={14} weight="bold" aria-hidden />
          Tendencia de viajes
        </span>
        <span className="nest-chip">Demo</span>
      </h3>
      <ResponsiveContainer width="100%" height={88}>
        <LineChart data={DEMO_TREND} margin={{ top: 4, right: 8, bottom: 0, left: 8 }}>
          <XAxis
            dataKey="t"
            tick={{ fontSize: 10, fill: "#674627" }}
            axisLine={{ stroke: "rgba(91,57,24,0.14)" }}
            tickLine={false}
          />
          <YAxis hide />
          <Tooltip
            contentStyle={{
              background: "#fffcf7",
              border: "1px solid rgba(91,57,24,0.14)",
              borderRadius: 8,
              fontSize: 11,
            }}
            labelStyle={{ color: "#674627" }}
          />
          <Line
            type="monotone"
            dataKey="viajes"
            stroke="#8a5a00"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: "#f9ae08" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </section>
  );
}
