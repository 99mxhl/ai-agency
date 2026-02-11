"use client";

import type { BrandOverview } from "@/types/audit";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { formatNumber } from "@/lib/format";
import { HealthGauge } from "./health-gauge";

interface BrandHeaderProps {
  brand: BrandOverview | null;
  healthScore: number | null;
  executiveSummary: string | null;
}

export function BrandHeader({ brand, healthScore, executiveSummary }: BrandHeaderProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start">
          {/* Brand info */}
          <div className="flex items-start gap-4 flex-1">
            <Avatar className="h-16 w-16">
              <AvatarImage src={brand?.profile_pic_url ?? undefined} alt={brand?.handle} />
              <AvatarFallback className="text-lg">
                {brand?.handle?.charAt(0).toUpperCase() ?? "?"}
              </AvatarFallback>
            </Avatar>
            <div className="space-y-1">
              <h1 className="text-2xl font-bold">@{brand?.handle ?? "unknown"}</h1>
              {brand?.followers_count != null && (
                <p className="text-sm text-muted-foreground">
                  {formatNumber(brand.followers_count)} followers
                </p>
              )}
              {brand?.bio && (
                <p className="text-sm text-muted-foreground max-w-md">
                  {brand.bio}
                </p>
              )}
            </div>
          </div>

          {/* Health gauge */}
          <div className="flex-shrink-0 self-center">
            <HealthGauge score={healthScore} />
          </div>
        </div>

        {/* Executive summary */}
        {executiveSummary && (
          <p className="mt-6 text-sm leading-relaxed text-muted-foreground border-t pt-4">
            {executiveSummary}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
