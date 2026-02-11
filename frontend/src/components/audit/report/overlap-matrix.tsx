"use client";

import type { AudienceOverlapEntry, InfluencerAnalysis } from "@/types/audit";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { formatPercentage } from "@/lib/format";

interface OverlapMatrixProps {
  overlaps: AudienceOverlapEntry[];
  influencers: InfluencerAnalysis[];
}

function abbreviate(handle: string): string {
  return handle.length > 8 ? handle.slice(0, 8) + "…" : handle;
}

function getCellColor(overlap: number): string {
  // Normalize: 5% = barely visible, 45%+ = max intensity
  const intensity = Math.min(Math.max((overlap - 5) / 40, 0), 1);
  // Warm ramp: subtle beige → red-orange warning
  const r = 239;
  const g = Math.round(239 - intensity * 139); // 239 → 100
  const b = Math.round(239 - intensity * 179); // 239 → 60
  return `rgb(${r}, ${g}, ${b})`;
}

export function OverlapMatrix({ overlaps, influencers }: OverlapMatrixProps) {
  // Build list of unique handles present in overlaps
  const handleSet = new Set<string>();
  overlaps.forEach((o) => {
    handleSet.add(o.influencer_a_handle);
    handleSet.add(o.influencer_b_handle);
  });
  const handles = influencers
    .map((i) => i.handle)
    .filter((h) => handleSet.has(h));

  // Build symmetric lookup: "a|b" → overlap %
  const lookup = new Map<string, number>();
  overlaps.forEach((o) => {
    lookup.set(`${o.influencer_a_handle}|${o.influencer_b_handle}`, o.overlap_percentage);
    lookup.set(`${o.influencer_b_handle}|${o.influencer_a_handle}`, o.overlap_percentage);
  });

  if (handles.length < 2) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        Not enough influencers to calculate audience overlap.
      </p>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-24" />
            {handles.map((h) => (
              <TableHead key={h} className="text-center text-xs px-2 min-w-[60px]">
                <Tooltip>
                  <TooltipTrigger className="cursor-default">
                    {abbreviate(h)}
                  </TooltipTrigger>
                  <TooltipContent>@{h}</TooltipContent>
                </Tooltip>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {handles.map((rowHandle) => (
            <TableRow key={rowHandle}>
              <TableCell className="text-xs font-medium whitespace-nowrap">
                <Tooltip>
                  <TooltipTrigger className="cursor-default">
                    {abbreviate(rowHandle)}
                  </TooltipTrigger>
                  <TooltipContent>@{rowHandle}</TooltipContent>
                </Tooltip>
              </TableCell>
              {handles.map((colHandle) => {
                if (rowHandle === colHandle) {
                  return (
                    <TableCell
                      key={colHandle}
                      className="text-center text-xs text-muted-foreground bg-muted/50"
                    >
                      —
                    </TableCell>
                  );
                }
                const value = lookup.get(`${rowHandle}|${colHandle}`);
                return (
                  <TableCell
                    key={colHandle}
                    className="text-center text-xs font-medium px-2"
                    style={{
                      backgroundColor: value != null ? getCellColor(value) : undefined,
                    }}
                  >
                    {value != null ? formatPercentage(value) : "—"}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
