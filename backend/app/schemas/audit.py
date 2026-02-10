from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AuditCreate(BaseModel):
    instagram_handle: str
    language: str = "en"


class AuditStatus(BaseModel):
    id: str
    status: str
    progress: int
    current_step: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InfluencerAnalysis(BaseModel):
    handle: str
    display_name: str | None = None
    profile_pic_url: str | None = None
    followers_count: int | None = None
    engagement_rate: float | None = None
    fraud_score: float | None = None
    fraud_indicators: dict | None = None
    content_quality_score: float | None = None
    audience_demographics: dict | None = None
    audience_quality_score: float | None = None
    estimated_reach: int | None = None
    discovery_source: str | None = None


class AudienceOverlapEntry(BaseModel):
    influencer_a_handle: str
    influencer_b_handle: str
    overlap_percentage: float


class BrandOverview(BaseModel):
    handle: str
    followers_count: int | None = None
    profile_pic_url: str | None = None
    bio: str | None = None


class AuditResult(BaseModel):
    id: str
    status: str
    progress: int
    current_step: str | None = None
    brand: BrandOverview | None = None
    health_score: float | None = None
    executive_summary: str | None = None
    recommendations: list[str] = Field(default_factory=list)
    influencers: list[InfluencerAnalysis] = Field(default_factory=list)
    audience_overlaps: list[AudienceOverlapEntry] = Field(default_factory=list)
    language: str = "en"
    created_at: datetime

    model_config = {"from_attributes": True}
