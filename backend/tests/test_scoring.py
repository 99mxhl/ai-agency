from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone

from app.data_sources.schemas import InfluencerProfileResult, PostData
from app.services.scoring import (
    calculate_audience_quality,
    calculate_content_quality,
    calculate_engagement_metrics,
    calculate_fraud_score,
    calculate_health_score,
    estimate_audience_overlap,
    estimate_reach_and_cpm,
)


# --- Fixtures ---


def _make_profile(
    followers: int = 10_000,
    following: int = 500,
    posts_count: int = 100,
    num_posts: int = 15,
    avg_likes: int = 500,
    avg_comments: int = 25,
    post_types: list[str] | None = None,
    caption_len: int = 120,
    hashtags_per_post: int = 6,
    spread_days: int = 60,
    is_verified: bool = False,
) -> InfluencerProfileResult:
    """Create a test profile with configurable characteristics."""
    now = datetime.now(timezone.utc)
    if post_types is None:
        post_types = ["image", "carousel", "reel", "video"]

    posts = []
    for i in range(num_posts):
        likes_variance = 0.8 + (i % 5) * 0.1  # some natural variance
        hashtags = [f"tag{j}" for j in range(hashtags_per_post)]
        posts.append(PostData(
            post_id=f"post_{i}",
            post_type=post_types[i % len(post_types)],
            caption="x" * caption_len + " " + " ".join(f"#{h}" for h in hashtags),
            likes_count=int(avg_likes * likes_variance),
            comments_count=int(avg_comments * likes_variance),
            timestamp=now - timedelta(days=spread_days * i / max(num_posts - 1, 1)),
            hashtags=hashtags,
        ))

    return InfluencerProfileResult(
        username="test_user",
        full_name="Test User",
        biography="Test bio",
        followers_count=followers,
        following_count=following,
        posts_count=posts_count,
        is_verified=is_verified,
        recent_posts=posts,
        raw_data={},
    )


def _make_suspicious_profile() -> InfluencerProfileResult:
    """Create a profile with suspicious characteristics."""
    return _make_profile(
        followers=200_000,
        following=5_000,
        avg_likes=100,       # very low for 200K followers
        avg_comments=1,      # almost no comments
        num_posts=15,
        caption_len=20,      # short captions
        hashtags_per_post=2,
        post_types=["image"],  # no diversity
    )


def _make_empty_profile() -> InfluencerProfileResult:
    """Create a profile with 0 posts and 0 followers."""
    return InfluencerProfileResult(
        username="empty_user",
        followers_count=0,
        following_count=0,
        posts_count=0,
        recent_posts=[],
        raw_data={},
    )


# --- calculate_engagement_metrics ---


class TestEngagementMetrics:
    def test_healthy_profile(self):
        profile = _make_profile(followers=10_000, avg_likes=500, avg_comments=25)
        result = calculate_engagement_metrics(profile)
        assert result["engagement_rate"] > 0
        assert result["avg_likes"] > 0
        assert result["avg_comments"] > 0

    def test_engagement_rate_formula(self):
        profile = _make_profile(
            followers=10_000, avg_likes=500, avg_comments=50, num_posts=1
        )
        result = calculate_engagement_metrics(profile)
        # (500 + 50) / 10000 = 0.055
        assert abs(result["engagement_rate"] - 0.044) < 0.01  # with variance

    def test_zero_followers(self):
        profile = _make_empty_profile()
        result = calculate_engagement_metrics(profile)
        assert result["engagement_rate"] == 0.0
        assert result["avg_likes"] == 0.0
        assert result["avg_comments"] == 0.0

    def test_zero_posts(self):
        profile = _make_profile(followers=10_000, num_posts=0)
        profile.recent_posts = []
        result = calculate_engagement_metrics(profile)
        assert result["engagement_rate"] == 0.0

    def test_output_structure(self):
        result = calculate_engagement_metrics(_make_profile())
        assert set(result.keys()) == {"engagement_rate", "avg_likes", "avg_comments"}


# --- calculate_fraud_score ---


class TestFraudScore:
    def test_healthy_profile_low_fraud(self):
        profile = _make_profile(followers=10_000, following=500, avg_likes=500, avg_comments=25)
        result = calculate_fraud_score(profile, 0.05, 500, 25)
        assert result["fraud_score"] < 0.3

    def test_suspicious_profile_high_fraud(self):
        profile = _make_suspicious_profile()
        # Very low engagement for 200K followers
        result = calculate_fraud_score(profile, 0.0005, 100, 1)
        assert result["fraud_score"] > 0.3

    def test_fraud_indicators_has_5_keys(self):
        profile = _make_profile()
        result = calculate_fraud_score(profile, 0.05, 500, 25)
        assert set(result["fraud_indicators"].keys()) == {
            "follower_following_ratio",
            "engagement_anomaly",
            "like_comment_ratio",
            "engagement_consistency",
            "posting_frequency",
        }

    def test_fraud_score_bounded(self):
        profile = _make_profile()
        result = calculate_fraud_score(profile, 0.05, 500, 25)
        assert 0.0 <= result["fraud_score"] <= 1.0

    def test_zero_followers(self):
        profile = _make_empty_profile()
        result = calculate_fraud_score(profile, 0.0, 0.0, 0.0)
        assert 0.0 <= result["fraud_score"] <= 1.0

    def test_high_following_ratio_suspicious(self):
        """More following than followers is suspicious."""
        profile = _make_profile(followers=100, following=5_000)
        result = calculate_fraud_score(profile, 0.05, 50, 5)
        assert result["fraud_indicators"]["follower_following_ratio"] > 0.0

    def test_output_structure(self):
        result = calculate_fraud_score(_make_profile(), 0.05, 500, 25)
        assert set(result.keys()) == {"fraud_score", "fraud_indicators"}


# --- calculate_content_quality ---


class TestContentQuality:
    def test_healthy_profile(self):
        profile = _make_profile(caption_len=150, hashtags_per_post=8, post_types=["image", "carousel", "reel"])
        result = calculate_content_quality(profile)
        assert result["content_quality_score"] > 0.5

    def test_poor_content(self):
        profile = _make_profile(caption_len=10, hashtags_per_post=0, post_types=["image"])
        result = calculate_content_quality(profile)
        assert result["content_quality_score"] < 0.5

    def test_zero_posts(self):
        profile = _make_empty_profile()
        result = calculate_content_quality(profile)
        assert result["content_quality_score"] == 0.0

    def test_content_analysis_has_4_keys(self):
        profile = _make_profile()
        result = calculate_content_quality(profile)
        assert set(result["content_analysis"].keys()) == {
            "caption_quality",
            "hashtag_usage",
            "posting_frequency",
            "media_type_diversity",
        }

    def test_score_bounded(self):
        profile = _make_profile()
        result = calculate_content_quality(profile)
        assert 0.0 <= result["content_quality_score"] <= 1.0

    def test_media_diversity_boost(self):
        """More media types → higher diversity score."""
        single = _make_profile(post_types=["image"])
        multi = _make_profile(post_types=["image", "carousel", "reel"])
        r1 = calculate_content_quality(single)
        r2 = calculate_content_quality(multi)
        assert r2["content_analysis"]["media_type_diversity"] > r1["content_analysis"]["media_type_diversity"]

    def test_output_structure(self):
        result = calculate_content_quality(_make_profile())
        assert set(result.keys()) == {"content_quality_score", "content_analysis"}


# --- calculate_audience_quality ---


class TestAudienceQuality:
    def test_high_engagement_low_fraud(self):
        profile = _make_profile(followers=10_000)
        result = calculate_audience_quality(profile, 0.06, 0.1)
        assert result["audience_quality_score"] > 0.7

    def test_low_engagement_high_fraud(self):
        profile = _make_profile(followers=200_000)
        result = calculate_audience_quality(profile, 0.002, 0.8)
        assert result["audience_quality_score"] < 0.3

    def test_demographics_populated(self):
        profile = _make_profile()
        result = calculate_audience_quality(profile, 0.05, 0.1)
        demo = result["audience_demographics"]
        assert "estimated_real_followers_pct" in demo
        assert "engagement_quality" in demo
        assert "follower_tier" in demo

    def test_score_bounded(self):
        profile = _make_profile()
        result = calculate_audience_quality(profile, 0.05, 0.5)
        assert 0.0 <= result["audience_quality_score"] <= 1.0

    def test_output_structure(self):
        result = calculate_audience_quality(_make_profile(), 0.05, 0.1)
        assert set(result.keys()) == {"audience_quality_score", "audience_demographics"}


# --- estimate_reach_and_cpm ---


class TestReachAndCpm:
    def test_nano_influencer(self):
        result = estimate_reach_and_cpm(5_000, 0.06, 0.8)
        assert result["estimated_reach"] > 0
        assert result["estimated_cpm"] > 0

    def test_macro_influencer(self):
        result = estimate_reach_and_cpm(1_000_000, 0.02, 0.7)
        assert result["estimated_reach"] > 0
        assert result["estimated_cpm"] > result["estimated_cpm"] * 0  # positive

    def test_zero_followers(self):
        result = estimate_reach_and_cpm(0, 0.0, 0.0)
        assert result["estimated_reach"] == 0
        assert result["estimated_cpm"] == 0.0

    def test_higher_engagement_more_reach(self):
        low = estimate_reach_and_cpm(50_000, 0.01, 0.5)
        high = estimate_reach_and_cpm(50_000, 0.08, 0.5)
        assert high["estimated_reach"] > low["estimated_reach"]

    def test_output_structure(self):
        result = estimate_reach_and_cpm(10_000, 0.05, 0.7)
        assert set(result.keys()) == {"estimated_reach", "estimated_cpm"}


# --- estimate_audience_overlap ---


class TestAudienceOverlap:
    def test_similar_profiles_higher_overlap(self):
        a = _make_profile(followers=10_000, hashtags_per_post=6)
        b = _make_profile(followers=12_000, hashtags_per_post=6)
        # Same hashtag patterns + similar size → higher overlap
        result = estimate_audience_overlap(a, b)
        assert result["overlap_percentage"] >= 5.0

    def test_different_profiles_lower_overlap(self):
        a = _make_profile(followers=5_000, hashtags_per_post=6)
        # Different hashtags
        b = _make_profile(followers=200_000, hashtags_per_post=6)
        for p in b.recent_posts:
            p.hashtags = [f"different_{h}" for h in p.hashtags]
        result = estimate_audience_overlap(a, b)
        assert result["overlap_percentage"] <= 45.0

    def test_overlap_bounded(self):
        a = _make_profile()
        b = _make_profile()
        result = estimate_audience_overlap(a, b)
        assert 5.0 <= result["overlap_percentage"] <= 45.0

    def test_empty_profiles(self):
        a = _make_empty_profile()
        b = _make_empty_profile()
        result = estimate_audience_overlap(a, b)
        assert result["overlap_percentage"] >= 5.0
        assert result["sample_size"] >= 100

    def test_output_structure(self):
        result = estimate_audience_overlap(_make_profile(), _make_profile())
        assert set(result.keys()) == {"overlap_percentage", "sample_size"}


# --- calculate_health_score ---


class TestHealthScore:
    def test_healthy_influencers(self):
        scores = [
            {"fraud_score": 0.1, "content_quality_score": 0.8, "audience_quality_score": 0.8, "engagement_rate": 0.05},
            {"fraud_score": 0.15, "content_quality_score": 0.7, "audience_quality_score": 0.75, "engagement_rate": 0.04},
        ]
        health = calculate_health_score(scores)
        assert health > 50

    def test_poor_influencers(self):
        scores = [
            {"fraud_score": 0.8, "content_quality_score": 0.2, "audience_quality_score": 0.2, "engagement_rate": 0.002},
            {"fraud_score": 0.9, "content_quality_score": 0.1, "audience_quality_score": 0.1, "engagement_rate": 0.001},
        ]
        health = calculate_health_score(scores)
        assert health < 30

    def test_empty_list(self):
        assert calculate_health_score([]) == 0.0

    def test_score_bounded(self):
        scores = [
            {"fraud_score": 0.0, "content_quality_score": 1.0, "audience_quality_score": 1.0, "engagement_rate": 0.10},
        ]
        health = calculate_health_score(scores)
        assert 0 <= health <= 100

    def test_single_perfect_influencer(self):
        scores = [
            {"fraud_score": 0.0, "content_quality_score": 1.0, "audience_quality_score": 1.0, "engagement_rate": 0.10},
        ]
        health = calculate_health_score(scores)
        assert health == 100.0
