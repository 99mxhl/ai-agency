"use client";

import { RadialBarChart, RadialBar, PolarAngleAxis } from "recharts";

interface HealthGaugeProps {
  score: number | null;
}

function getGaugeColor(score: number): string {
  if (score >= 70) return "hsl(142, 71%, 45%)"; // green
  if (score >= 40) return "hsl(38, 92%, 50%)"; // amber
  return "hsl(0, 84%, 60%)"; // red
}

function getLabel(score: number): string {
  if (score >= 70) return "Healthy";
  if (score >= 40) return "Needs Work";
  return "At Risk";
}

export function HealthGauge({ score }: HealthGaugeProps) {
  const value = score ?? 0;
  const color = getGaugeColor(value);
  const label = score != null ? getLabel(value) : "N/A";

  const data = [{ value, fill: color }];

  return (
    <div className="relative flex flex-col items-center">
      <RadialBarChart
        width={160}
        height={100}
        cx={80}
        cy={90}
        innerRadius={60}
        outerRadius={80}
        barSize={12}
        data={data}
        startAngle={180}
        endAngle={0}
      >
        <PolarAngleAxis
          type="number"
          domain={[0, 100]}
          angleAxisId={0}
          tick={false}
        />
        <RadialBar
          dataKey="value"
          cornerRadius={6}
          background={{ fill: "hsl(var(--muted))" }}
        />
      </RadialBarChart>
      {/* Centered score */}
      <div className="absolute bottom-0 flex flex-col items-center">
        <span className="text-2xl font-bold" style={{ color }}>
          {score != null ? Math.round(score) : "—"}
        </span>
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
    </div>
  );
}
