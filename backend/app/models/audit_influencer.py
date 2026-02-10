from __future__ import annotations

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class AuditInfluencer(Base):
    __tablename__ = "audit_influencers"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    audit_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("audits.id"), nullable=False, index=True
    )
    influencer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("influencers.id"), nullable=False, index=True
    )
    discovery_source: Mapped[str] = mapped_column(String(100), nullable=False)
    engagement_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_likes: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_comments: Mapped[float | None] = mapped_column(Float, nullable=True)
    fraud_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fraud_indicators: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    content_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    content_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    audience_demographics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    audience_quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_reach: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cpm: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    audit = relationship("Audit", lazy="selectin")
    influencer = relationship("Influencer", lazy="selectin")
