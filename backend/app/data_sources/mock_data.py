from __future__ import annotations

import hashlib
import random

from app.data_sources.schemas import (
    BrandProfileResult,
    DiscoveredInfluencer,
    InfluencerDiscoveryResult,
)

# Realistic-looking mock usernames
_INFLUENCER_POOLS = {
    "tagged_posts": [
        "lifestyle.anna", "fitcoach_mike", "beauty.daily.pl", "travel.kate",
        "foodie_adventures", "style.with.emma", "wellness_guru", "tech.reviews.pl",
        "home.inspo.daily", "mama.blogger.cz",
    ],
    "related_profiles": [
        "brand.collab.hub", "digital.native.ro", "content.creator.pl",
        "social.media.pro", "influencer.daily", "creator.economy",
        "viral.content.cz", "trending.now.pl",
    ],
    "hashtag_search": [
        "skincare.routine.daily", "ootd.polska", "healthyliving.cz",
        "makeup.tutorials.ro", "gym.motivation.pl", "vegan.eats.europe",
        "diy.home.decor", "book.club.cee", "pet.lovers.daily", "eco.living.pl",
    ],
}


def _seed_from_handle(handle: str) -> random.Random:
    """Create a deterministic RNG seeded from the handle."""
    seed = int(hashlib.md5(handle.encode()).hexdigest(), 16)  # noqa: S324
    return random.Random(seed)


def generate_mock_brand_profile(handle: str) -> BrandProfileResult:
    """Generate a realistic mock brand profile, deterministic per handle."""
    rng = _seed_from_handle(handle)

    followers = rng.randint(5_000, 500_000)
    following = rng.randint(200, 2_000)
    posts = rng.randint(50, 2_000)

    bios = [
        f"Official {handle.replace('.', ' ').title()} | Delivering quality since 2015",
        f"{handle.replace('.', ' ').title()} - Your trusted partner in CEE",
        f"We are {handle.replace('.', ' ').title()} | Innovation meets tradition",
        f"{handle.replace('.', ' ').title()} | Premium products for everyday life",
    ]

    return BrandProfileResult(
        username=handle,
        full_name=handle.replace(".", " ").replace("_", " ").title(),
        biography=rng.choice(bios),
        followers_count=followers,
        following_count=following,
        posts_count=posts,
        profile_pic_url=f"https://mock-cdn.example.com/profiles/{handle}.jpg",
        is_verified=rng.random() > 0.6,
        is_business=True,
        raw_data={"source": "mock", "handle": handle},
    )


def generate_mock_discovered_influencers(handle: str) -> InfluencerDiscoveryResult:
    """Generate 8-15 mock influencers distributed across all 3 discovery sources."""
    rng = _seed_from_handle(handle + "_discovery")
    total_count = rng.randint(8, 15)

    # Distribute across sources: ~40% tagged, ~30% related, ~30% hashtag
    tagged_count = max(2, int(total_count * 0.4))
    related_count = max(2, int(total_count * 0.3))
    hashtag_count = total_count - tagged_count - related_count

    influencers: list[DiscoveredInfluencer] = []
    seen_usernames: set[str] = set()

    for source, count, pool in [
        ("tagged_posts", tagged_count, _INFLUENCER_POOLS["tagged_posts"]),
        ("related_profiles", related_count, _INFLUENCER_POOLS["related_profiles"]),
        ("hashtag_search", hashtag_count, _INFLUENCER_POOLS["hashtag_search"]),
    ]:
        available = [u for u in pool if u != handle and u not in seen_usernames]
        picked = rng.sample(available, min(count, len(available)))

        for username in picked:
            seen_usernames.add(username)
            influencers.append(
                DiscoveredInfluencer(
                    username=username,
                    followers_count=rng.randint(1_000, 200_000),
                    discovery_source=source,
                    discovery_context=f"Mock discovery via {source} for @{handle}",
                )
            )

    return InfluencerDiscoveryResult(
        influencers=influencers,
        sources_attempted=["tagged_posts", "related_profiles", "hashtag_search"],
        sources_succeeded=["tagged_posts", "related_profiles", "hashtag_search"],
        sources_failed=[],
        errors=[],
    )
