export function formatNumber(n: number | null | undefined): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

export function formatPercentage(n: number | null | undefined): string {
  if (n == null) return "—";
  return `${n.toFixed(1)}%`;
}

export type ScoreColor = "green" | "yellow" | "red";

export function getScoreColor(
  value: number | null | undefined,
  thresholds: { green: number; yellow: number },
  inverted = false,
): ScoreColor {
  if (value == null) return "red";
  if (inverted) {
    if (value <= thresholds.yellow) return "green";
    if (value <= thresholds.green) return "yellow";
    return "red";
  }
  if (value >= thresholds.green) return "green";
  if (value >= thresholds.yellow) return "yellow";
  return "red";
}

export const SCORE_COLOR_MAP: Record<ScoreColor, string> = {
  green: "bg-emerald-100 text-emerald-800",
  yellow: "bg-amber-100 text-amber-800",
  red: "bg-red-100 text-red-800",
};
