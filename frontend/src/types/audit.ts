export interface BrandOverview {
  handle: string;
  followers_count: number | null;
  profile_pic_url: string | null;
  bio: string | null;
}

export interface InfluencerAnalysis {
  handle: string;
  display_name: string | null;
  profile_pic_url: string | null;
  followers_count: number | null;
  engagement_rate: number | null;
  fraud_score: number | null;
  fraud_indicators: Record<string, unknown> | null;
  content_quality_score: number | null;
  audience_demographics: Record<string, unknown> | null;
  audience_quality_score: number | null;
  estimated_reach: number | null;
  discovery_source: string | null;
}

export interface AudienceOverlapEntry {
  influencer_a_handle: string;
  influencer_b_handle: string;
  overlap_percentage: number;
}

export interface AuditResult {
  id: string;
  status: string;
  progress: number;
  current_step: string | null;
  brand: BrandOverview | null;
  health_score: number | null;
  executive_summary: string | null;
  recommendations: string[];
  influencers: InfluencerAnalysis[];
  audience_overlaps: AudienceOverlapEntry[];
  language: string;
  created_at: string;
}

export interface AuditCreate {
  instagram_handle: string;
  language?: string;
}

export interface AuditStatus {
  id: string;
  status: string;
  progress: number;
  current_step: string | null;
  created_at: string;
}

export type AuditStatusType =
  | "pending"
  | "scraping_brand"
  | "discovering_influencers"
  | "analyzing_influencers"
  | "scoring"
  | "generating_narrative"
  | "completed"
  | "failed";

export const PIPELINE_STEPS: { status: AuditStatusType; label: string; progress: number }[] = [
  { status: "scraping_brand", label: "Scraping brand profile", progress: 15 },
  { status: "discovering_influencers", label: "Discovering influencers", progress: 30 },
  { status: "analyzing_influencers", label: "Analyzing profiles", progress: 55 },
  { status: "scoring", label: "Calculating scores", progress: 75 },
  { status: "generating_narrative", label: "Generating narrative", progress: 90 },
  { status: "completed", label: "Audit complete", progress: 100 },
];
