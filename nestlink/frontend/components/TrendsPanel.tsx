"use client";

/**
 * Panel de tendencias con Recharts.
 * TODO: conectar a GET /api/v1/metrics para histórico real de viajes y ROI.
 */
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const DEMO_TREND = [
  { t: "10:00", viajes: 4, roi: 12 },
  { t: "11:00", viajes: 8, roi: 15 },
  { t: "12:00", viajes: 12, roi: 18 },
  { t: "13:00", viajes: 15, roi: 20 },
  { t: "14:00", viajes: 18, roi: 22 },
];

export function TrendsPanel() {
  return (
    <div className="nest-panel hidden lg:block shrink-0 p-3">
      <div className="nest-label mb-2">Tendencia de viajes</div>
      <ResponsiveContainer width="100%" height={72}>
        <LineChart data={DEMO_TREND}>
          <XAxis
            dataKey="t"
            tick={{ fontSize: 10, fill: "#6b7280" }}
            axisLine={{ stroke: "rgba(15,23,42,0.08)" }}
            tickLine={false}
          />
          <YAxis hide />
          <Tooltip
            contentStyle={{
              background: "#ffffff",
              border: "1px solid rgba(15,23,42,0.1)",
              borderRadius: 8,
              fontSize: 11,
            }}
            labelStyle={{ color: "#6b7280" }}
          />
          <Line
            type="monotone"
            dataKey="viajes"
            stroke="#e4032e"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: "#e4032e" }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
