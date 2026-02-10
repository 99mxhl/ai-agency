from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class BrandProfileResult:
    username: str
    full_name: str | None = None
    biography: str | None = None
    followers_count: int | None = None
    following_count: int | None = None
    posts_count: int | None = None
    profile_pic_url: str | None = None
    is_verified: bool = False
    is_business: bool = False
    raw_data: dict = field(default_factory=dict)


DiscoverySource = Literal["tagged_posts", "related_profiles", "hashtag_search"]


@dataclass
class DiscoveredInfluencer:
    username: str
    followers_count: int | None = None
    discovery_source: DiscoverySource = "tagged_posts"
    discovery_context: str = ""


@dataclass
class InfluencerDiscoveryResult:
    influencers: list[DiscoveredInfluencer] = field(default_factory=list)
    sources_attempted: list[str] = field(default_factory=list)
    sources_succeeded: list[str] = field(default_factory=list)
    sources_failed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
