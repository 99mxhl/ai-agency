"use client";

import type { InfluencerAnalysis } from "@/types/audit";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ScoreBadge } from "./score-badge";
import { formatNumber } from "@/lib/format";
import { AlertTriangle } from "lucide-react";

interface InfluencerCardProps {
  influencer: InfluencerAnalysis;
}

function formatFraudIndicators(indicators: Record<string, unknown> | null): string {
  if (!indicators) return "No fraud data available";
  const entries = Object.entries(indicators)
    .filter(([, v]) => v === true || (typeof v === "number" && v > 0))
    .map(([k]) => k.replace(/_/g, " "));
  return entries.length > 0 ? entries.join(", ") : "No fraud signals detected";
}

export function InfluencerCard({ influencer }: InfluencerCardProps) {
  // Backend returns scores on 0-1 scale — convert to 0-100 for display
  const engagementPct = influencer.engagement_rate != null ? influencer.engagement_rate * 100 : null;
  const fraudPct = influencer.fraud_score != null ? influencer.fraud_score * 100 : null;
  const contentPct = influencer.content_quality_score != null ? influencer.content_quality_score * 100 : null;
  const audiencePct = influencer.audience_quality_score != null ? influencer.audience_quality_score * 100 : null;

  const hasFraudWarning = fraudPct != null && fraudPct > 50;

  return (
    <Card className="relative overflow-hidden">
      <CardContent className="pt-6 space-y-4">
        {/* Header */}
        <div className="flex items-start gap-3">
          <Avatar className="h-10 w-10">
            <AvatarImage
              src={influencer.profile_pic_url ?? undefined}
              alt={influencer.handle}
            />
            <AvatarFallback>
              {influencer.handle.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium truncate">
                @{influencer.handle}
              </p>
              {hasFraudWarning && (
                <Tooltip>
                  <TooltipTrigger>
                    <AlertTriangle className="h-3.5 w-3.5 text-red-500" />
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs text-xs">
                      {formatFraudIndicators(influencer.fraud_indicators)}
                    </p>
                  </TooltipContent>
                </Tooltip>
              )}
            </div>
            {influencer.display_name && (
              <p className="text-xs text-muted-foreground truncate">
                {influencer.display_name}
              </p>
            )}
            <p className="text-xs text-muted-foreground">
              {formatNumber(influencer.followers_count)} followers
            </p>
          </div>
        </div>

        {/* Score badges */}
        <div className="flex flex-wrap gap-1.5">
          <ScoreBadge
            label="Eng"
            value={engagementPct}
            format="percentage"
            thresholds={{ green: 3, yellow: 1 }}
          />
          <ScoreBadge
            label="Fraud"
            value={fraudPct}
            thresholds={{ green: 50, yellow: 20 }}
            inverted
            tooltip={formatFraudIndicators(influencer.fraud_indicators)}
          />
          <ScoreBadge
            label="Content"
            value={contentPct}
            thresholds={{ green: 70, yellow: 40 }}
          />
          <ScoreBadge
            label="Audience"
            value={audiencePct}
            thresholds={{ green: 70, yellow: 40 }}
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          {influencer.estimated_reach != null && (
            <span>Est. reach: {formatNumber(influencer.estimated_reach)}</span>
          )}
          {influencer.discovery_source && (
            <Badge variant="outline" className="text-xs h-5">
              {influencer.discovery_source.replace(/_/g, " ")}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
