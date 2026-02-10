from __future__ import annotations

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    brand_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("brands.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", server_default=text("'pending'")
    )
    progress: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    current_step: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(
        String(10), nullable=False, default="en", server_default=text("'en'")
    )
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    influencer_insights: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    brand = relationship("Brand", lazy="selectin")
