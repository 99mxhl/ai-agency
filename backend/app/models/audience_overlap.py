from __future__ import annotations

from sqlalchemy import DateTime, Float, ForeignKey, Integer, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class AudienceOverlap(Base):
    __tablename__ = "audience_overlaps"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    audit_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("audits.id"), nullable=False, index=True
    )
    influencer_a_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("influencers.id"), nullable=False, index=True
    )
    influencer_b_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("influencers.id"), nullable=False, index=True
    )
    overlap_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    audit = relationship("Audit", lazy="selectin")
    influencer_a = relationship("Influencer", foreign_keys=[influencer_a_id], lazy="selectin")
    influencer_b = relationship("Influencer", foreign_keys=[influencer_b_id], lazy="selectin")
