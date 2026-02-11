"use client";

import type { AuditResult } from "@/types/audit";
import { BrandHeader } from "./brand-header";
import { InfluencerGrid } from "./influencer-grid";
import { OverlapMatrix } from "./overlap-matrix";
import { RecommendationsStub } from "./recommendations-stub";
import { ReportCta } from "./report-cta";
import { Separator } from "@/components/ui/separator";

interface ReportLayoutProps {
  audit: AuditResult;
}

const NAV_ITEMS = [
  { id: "overview", label: "Overview" },
  { id: "influencers", label: "Influencers" },
  { id: "overlap", label: "Overlap" },
];

export function ReportLayout({ audit }: ReportLayoutProps) {
  return (
    <div className="min-h-screen bg-muted/30">
      {/* Sticky nav */}
      <nav className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-5xl items-center gap-6 px-4 py-3">
          <span className="text-sm font-semibold">Brand Audit</span>
          <div className="flex gap-4">
            {NAV_ITEMS.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {item.label}
              </a>
            ))}
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-5xl space-y-10 px-4 py-8">
        {/* Overview */}
        <section id="overview">
          <BrandHeader
            brand={audit.brand}
            healthScore={audit.health_score}
            executiveSummary={audit.executive_summary}
          />
        </section>

        <Separator />

        {/* Influencers */}
        <section id="influencers" className="space-y-4">
          <h2 className="text-xl font-semibold">
            Influencer Analysis
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              ({audit.influencers.length} found)
            </span>
          </h2>
          <InfluencerGrid influencers={audit.influencers} />
        </section>

        <Separator />

        {/* Overlap */}
        {audit.audience_overlaps.length > 0 && (
          <section id="overlap" className="space-y-4">
            <h2 className="text-xl font-semibold">Audience Overlap</h2>
            <OverlapMatrix
              overlaps={audit.audience_overlaps}
              influencers={audit.influencers}
            />
          </section>
        )}

        <Separator />

        {/* Recommendations */}
        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Recommendations</h2>
          <RecommendationsStub />
        </section>

        <Separator />

        {/* CTA */}
        <ReportCta />
      </main>
    </div>
  );
}
