import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { getScoreColor, SCORE_COLOR_MAP, formatPercentage } from "@/lib/format";
import { cn } from "@/lib/utils";

interface ScoreBadgeProps {
  label: string;
  value: number | null;
  format?: "percentage" | "score";
  thresholds: { green: number; yellow: number };
  inverted?: boolean;
  tooltip?: string;
}

export function ScoreBadge({
  label,
  value,
  format = "score",
  thresholds,
  inverted = false,
  tooltip,
}: ScoreBadgeProps) {
  const color = getScoreColor(value, thresholds, inverted);
  const displayValue =
    value == null
      ? "—"
      : format === "percentage"
        ? formatPercentage(value)
        : Math.round(value).toString();

  const badge = (
    <Badge variant="secondary" className={cn("gap-1.5 font-normal", SCORE_COLOR_MAP[color])}>
      <span className="text-xs text-inherit/70">{label}</span>
      <span className="font-medium">{displayValue}</span>
    </Badge>
  );

  if (tooltip) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{badge}</TooltipTrigger>
        <TooltipContent>
          <p className="max-w-xs text-xs">{tooltip}</p>
        </TooltipContent>
      </Tooltip>
    );
  }

  return badge;
}
