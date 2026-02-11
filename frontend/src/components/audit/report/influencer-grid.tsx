import type { InfluencerAnalysis } from "@/types/audit";
import { InfluencerCard } from "./influencer-card";

interface InfluencerGridProps {
  influencers: InfluencerAnalysis[];
}

export function InfluencerGrid({ influencers }: InfluencerGridProps) {
  if (influencers.length === 0) {
    return (
      <p className="text-sm text-muted-foreground py-8 text-center">
        No influencers were discovered for this brand.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {influencers.map((influencer) => (
        <InfluencerCard key={influencer.handle} influencer={influencer} />
      ))}
    </div>
  );
}
