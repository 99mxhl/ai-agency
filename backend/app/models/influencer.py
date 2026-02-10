from __future__ import annotations

from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    instagram_handle: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    followers_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    following_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    posts_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    profile_pic_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_scraped_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[str | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
