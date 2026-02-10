from __future__ import annotations

import hashlib
import re
import random
from datetime import datetime, timedelta, timezone

from app.data_sources.schemas import (
    BrandProfileResult,
    DiscoveredInfluencer,
    InfluencerDiscoveryResult,
    InfluencerProfileResult,
    PostData,
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


# Hashtag pools for generating realistic post captions
_HASHTAG_POOLS = [
    "fitness", "lifestyle", "ootd", "beauty", "travel", "food", "health",
    "skincare", "fashion", "motivation", "workout", "vegan", "photography",
    "nature", "art", "wellness", "selfcare", "style", "inspo", "polska",
    "romania", "czechia", "europe", "cee", "influencer", "collab",
]

_CAPTION_TEMPLATES = [
    "Loving this new {topic}! What do you think? {hashtags}",
    "Another beautiful day {activity} {hashtags}",
    "Can't get enough of this {topic} {hashtags}",
    "New post! {topic} vibes {hashtags}",
    "Weekend mood: {activity} {hashtags}",
    "{topic} goals! Link in bio {hashtags}",
    "Just sharing my {topic} journey {hashtags}",
    "Who else loves {topic}? Drop a comment! {hashtags}",
    "Swipe for more {topic} content {hashtags}",
    "Grateful for this {topic} moment {hashtags}",
]

_TOPICS = [
    "skincare routine", "fitness journey", "travel adventure", "recipe",
    "outfit", "home decor", "morning routine", "workout plan",
    "beauty look", "wellness tip",
]

_ACTIVITIES = [
    "exploring the city", "at the gym", "cooking healthy meals",
    "shopping for new outfits", "hiking in nature",
    "working on content", "trying new products",
]


def generate_mock_influencer_profile(handle: str) -> InfluencerProfileResult:
    """Generate a realistic mock influencer profile with posts, deterministic per handle."""
    rng = _seed_from_handle(handle + "_profile")

    # ~20% chance of suspicious (inflated followers, low engagement)
    is_suspicious = rng.random() < 0.20

    if is_suspicious:
        followers = rng.randint(50_000, 500_000)
        following = rng.randint(3_000, 7_500)  # high following ratio
        base_engagement_pct = rng.uniform(0.002, 0.008)  # very low engagement
    else:
        followers = rng.randint(1_000, 200_000)
        following = rng.randint(100, 2_000)
        base_engagement_pct = rng.uniform(0.02, 0.08)

    posts_count = rng.randint(50, 800)
    num_recent_posts = rng.randint(12, 20)

    # Generate post type distribution: 50% image, 20% carousel, 20% reel, 10% video
    post_type_weights = [("image", 50), ("carousel", 20), ("reel", 20), ("video", 10)]
    post_types_pool = []
    for pt, weight in post_type_weights:
        post_types_pool.extend([pt] * weight)

    now = datetime.now(timezone.utc)
    spread_days = rng.randint(30, 90)

    # Pick hashtags for this influencer
    num_hashtags_per_post = rng.randint(3, 8)
    influencer_hashtags = rng.sample(_HASHTAG_POOLS, min(12, len(_HASHTAG_POOLS)))

    recent_posts: list[PostData] = []
    for i in range(num_recent_posts):
        post_type = rng.choice(post_types_pool)

        # Engagement varies per post (some variance around base)
        engagement_mult = rng.uniform(0.5, 1.8)
        likes = max(1, int(followers * base_engagement_pct * engagement_mult))
        comments = max(0, int(likes * rng.uniform(0.02, 0.10)))

        # Timestamp spread over the date range
        days_ago = spread_days * (i / max(num_recent_posts - 1, 1))
        timestamp = now - timedelta(days=days_ago, hours=rng.randint(0, 23))

        # Caption with hashtags
        post_hashtags = rng.sample(
            influencer_hashtags, min(num_hashtags_per_post, len(influencer_hashtags))
        )
        hashtag_str = " ".join(f"#{h}" for h in post_hashtags)
        caption = rng.choice(_CAPTION_TEMPLATES).format(
            topic=rng.choice(_TOPICS),
            activity=rng.choice(_ACTIVITIES),
            hashtags=hashtag_str,
        )

        recent_posts.append(PostData(
            post_id=f"mock_{handle}_{i}",
            post_type=post_type,
            caption=caption,
            likes_count=likes,
            comments_count=comments,
            timestamp=timestamp,
            hashtags=post_hashtags,
        ))

    bios = [
        f"{handle.replace('.', ' ').replace('_', ' ').title()} | Content Creator",
        f"Living my best life | {handle.replace('.', ' ').title()}",
        f"Sharing {rng.choice(_TOPICS)} tips | DM for collabs",
        f"Creator from CEE | {rng.choice(['PL', 'RO', 'CZ'])} based",
    ]

    return InfluencerProfileResult(
        username=handle,
        full_name=handle.replace(".", " ").replace("_", " ").title(),
        biography=rng.choice(bios),
        followers_count=followers,
        following_count=following,
        posts_count=posts_count,
        profile_pic_url=f"https://mock-cdn.example.com/profiles/{handle}.jpg",
        is_verified=rng.random() > 0.85,
        recent_posts=recent_posts,
        raw_data={"source": "mock", "handle": handle},
    )
