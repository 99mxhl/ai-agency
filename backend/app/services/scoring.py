"""Pure scoring functions — no DB, no async, no side effects.

All functions take dataclass instances or primitive values and return dicts.
Independently unit-testable.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.data_sources.schemas import InfluencerProfileResult


def calculate_engagement_metrics(
    profile: InfluencerProfileResult,
) -> dict:
    """Calculate engagement rate, average likes, and average comments from recent posts.

    Returns:
        {engagement_rate: float, avg_likes: float, avg_comments: float}
    """
    posts = profile.recent_posts
    followers = profile.followers_count or 0

    if not posts or followers == 0:
        return {"engagement_rate": 0.0, "avg_likes": 0.0, "avg_comments": 0.0}

    total_likes = sum(p.likes_count for p in posts)
    total_comments = sum(p.comments_count for p in posts)
    n = len(posts)

    avg_likes = total_likes / n
    avg_comments = total_comments / n
    engagement_rate = (avg_likes + avg_comments) / followers

    return {
        "engagement_rate": round(engagement_rate, 6),
        "avg_likes": round(avg_likes, 2),
        "avg_comments": round(avg_comments, 2),
    }


def calculate_fraud_score(
    profile: InfluencerProfileResult,
    engagement_rate: float,
    avg_likes: float,
    avg_comments: float,
) -> dict:
    """Detect suspicious accounts via 5 weighted signals.

    Returns:
        {fraud_score: float 0-1, fraud_indicators: dict}

    Signals:
        - follower_following_ratio (0.20): Abnormally low ratio suggests bought followers
        - engagement_anomaly (0.25): Very low or very high engagement is suspicious
        - like_comment_ratio (0.20): Real accounts have ~2-5% comment-to-like ratio
        - engagement_consistency (0.20): Uniform engagement across posts is suspicious
        - posting_frequency (0.15): Very irregular posting suggests bot behavior
    """
    followers = profile.followers_count or 0
    following = profile.following_count or 0
    posts = profile.recent_posts

    indicators: dict = {}

    # 1. Follower/following ratio (0.20)
    if following > 0:
        ratio = followers / following
        if ratio < 1.0:
            # More following than followers — suspicious
            indicators["follower_following_ratio"] = min(1.0, (1.0 - ratio))
        elif ratio > 100:
            # Extremely high ratio can indicate bought followers
            indicators["follower_following_ratio"] = min(1.0, (ratio - 100) / 500)
        else:
            indicators["follower_following_ratio"] = 0.0
    else:
        indicators["follower_following_ratio"] = 0.5  # no data

    # 2. Engagement anomaly (0.25)
    if followers > 0:
        if engagement_rate < 0.005:
            # Very low engagement — likely fake followers
            indicators["engagement_anomaly"] = min(1.0, (0.005 - engagement_rate) / 0.005)
        elif engagement_rate > 0.20:
            # Suspiciously high — possible engagement pods
            indicators["engagement_anomaly"] = min(1.0, (engagement_rate - 0.20) / 0.30)
        else:
            indicators["engagement_anomaly"] = 0.0
    else:
        indicators["engagement_anomaly"] = 0.5

    # 3. Like/comment ratio (0.20)
    if avg_likes > 0:
        comment_ratio = avg_comments / avg_likes
        if comment_ratio < 0.01:
            # Almost no comments — suspicious
            indicators["like_comment_ratio"] = min(1.0, (0.01 - comment_ratio) / 0.01)
        elif comment_ratio > 0.20:
            # Too many comments relative to likes — comment bots
            indicators["like_comment_ratio"] = min(1.0, (comment_ratio - 0.20) / 0.30)
        else:
            indicators["like_comment_ratio"] = 0.0
    else:
        indicators["like_comment_ratio"] = 0.3  # no data, slight suspicion

    # 4. Engagement consistency (0.20) — std dev of likes
    if len(posts) >= 3:
        likes_list = [p.likes_count for p in posts]
        mean_likes = sum(likes_list) / len(likes_list)
        if mean_likes > 0:
            variance = sum((x - mean_likes) ** 2 for x in likes_list) / len(likes_list)
            cv = math.sqrt(variance) / mean_likes  # coefficient of variation
            if cv < 0.10:
                # Almost identical likes across posts — bot-like
                indicators["engagement_consistency"] = min(1.0, (0.10 - cv) / 0.10)
            else:
                indicators["engagement_consistency"] = 0.0
        else:
            indicators["engagement_consistency"] = 0.3
    else:
        indicators["engagement_consistency"] = 0.3  # not enough data

    # 5. Posting frequency (0.15) — regularity of timestamps
    if len(posts) >= 3:
        timestamps = [p.timestamp for p in posts if p.timestamp]
        if len(timestamps) >= 3:
            timestamps_sorted = sorted(timestamps)
            gaps = [
                (timestamps_sorted[i + 1] - timestamps_sorted[i]).total_seconds()
                for i in range(len(timestamps_sorted) - 1)
            ]
            mean_gap = sum(gaps) / len(gaps)
            if mean_gap > 0:
                gap_cv = (
                    math.sqrt(sum((g - mean_gap) ** 2 for g in gaps) / len(gaps))
                    / mean_gap
                )
                # Very regular posting = bot. But also very irregular = suspicious
                if gap_cv < 0.05:
                    indicators["posting_frequency"] = 0.8
                elif gap_cv > 3.0:
                    indicators["posting_frequency"] = min(1.0, (gap_cv - 3.0) / 5.0)
                else:
                    indicators["posting_frequency"] = 0.0
            else:
                indicators["posting_frequency"] = 0.5
        else:
            indicators["posting_frequency"] = 0.3
    else:
        indicators["posting_frequency"] = 0.3

    # Weighted composite
    weights = {
        "follower_following_ratio": 0.20,
        "engagement_anomaly": 0.25,
        "like_comment_ratio": 0.20,
        "engagement_consistency": 0.20,
        "posting_frequency": 0.15,
    }

    fraud_score = sum(indicators[k] * weights[k] for k in weights)
    fraud_score = round(max(0.0, min(1.0, fraud_score)), 4)

    return {"fraud_score": fraud_score, "fraud_indicators": indicators}


def calculate_content_quality(
    profile: InfluencerProfileResult,
) -> dict:
    """Evaluate content quality via 4 weighted signals.

    Returns:
        {content_quality_score: float 0-1, content_analysis: dict}

    Signals:
        - caption_quality (0.30): Length, hashtag usage in captions
        - hashtag_usage (0.20): Optimal range of hashtags per post
        - posting_frequency (0.25): Regular posting schedule
        - media_type_diversity (0.25): Mix of images, videos, carousels, reels
    """
    posts = profile.recent_posts
    analysis: dict = {}

    if not posts:
        return {
            "content_quality_score": 0.0,
            "content_analysis": {
                "caption_quality": 0.0,
                "hashtag_usage": 0.0,
                "posting_frequency": 0.0,
                "media_type_diversity": 0.0,
            },
        }

    # 1. Caption quality (0.30) — based on caption length
    caption_lengths = [len(p.caption) for p in posts]
    avg_caption_len = sum(caption_lengths) / len(caption_lengths)
    if avg_caption_len >= 100:
        analysis["caption_quality"] = min(1.0, avg_caption_len / 300)
    elif avg_caption_len >= 30:
        analysis["caption_quality"] = avg_caption_len / 100
    else:
        analysis["caption_quality"] = max(0.1, avg_caption_len / 100)

    # 2. Hashtag usage (0.20) — sweet spot is 5-15 hashtags per post
    hashtag_counts = [len(p.hashtags) for p in posts]
    avg_hashtags = sum(hashtag_counts) / len(hashtag_counts)
    if 5 <= avg_hashtags <= 15:
        analysis["hashtag_usage"] = 1.0
    elif avg_hashtags < 5:
        analysis["hashtag_usage"] = max(0.2, avg_hashtags / 5)
    else:
        analysis["hashtag_usage"] = max(0.3, 1.0 - (avg_hashtags - 15) / 20)

    # 3. Posting frequency (0.25) — based on posts per week
    timestamps = [p.timestamp for p in posts if p.timestamp]
    if len(timestamps) >= 2:
        timestamps_sorted = sorted(timestamps)
        span = (timestamps_sorted[-1] - timestamps_sorted[0]).total_seconds()
        weeks = max(span / (7 * 24 * 3600), 0.1)
        posts_per_week = len(timestamps) / weeks
        if 2 <= posts_per_week <= 7:
            analysis["posting_frequency"] = 1.0
        elif posts_per_week < 2:
            analysis["posting_frequency"] = max(0.2, posts_per_week / 2)
        else:
            analysis["posting_frequency"] = max(0.4, 1.0 - (posts_per_week - 7) / 14)
    else:
        analysis["posting_frequency"] = 0.3

    # 4. Media type diversity (0.25) — number of unique types used
    types_used = {p.post_type for p in posts}
    type_count = len(types_used)
    if type_count >= 3:
        analysis["media_type_diversity"] = 1.0
    elif type_count == 2:
        analysis["media_type_diversity"] = 0.7
    else:
        analysis["media_type_diversity"] = 0.3

    weights = {
        "caption_quality": 0.30,
        "hashtag_usage": 0.20,
        "posting_frequency": 0.25,
        "media_type_diversity": 0.25,
    }

    score = sum(analysis[k] * weights[k] for k in weights)
    score = round(max(0.0, min(1.0, score)), 4)

    return {"content_quality_score": score, "content_analysis": analysis}


def calculate_audience_quality(
    profile: InfluencerProfileResult,
    engagement_rate: float,
    fraud_score: float,
) -> dict:
    """Estimate audience quality based on engagement and fraud signals.

    Returns:
        {audience_quality_score: float 0-1, audience_demographics: dict}
    """
    followers = profile.followers_count or 0

    # Base quality from engagement rate (higher = better audience)
    if engagement_rate >= 0.05:
        base_quality = 0.9
    elif engagement_rate >= 0.03:
        base_quality = 0.7
    elif engagement_rate >= 0.01:
        base_quality = 0.5
    else:
        base_quality = 0.2

    # Penalize by fraud score
    quality = base_quality * (1 - fraud_score * 0.8)
    quality = round(max(0.0, min(1.0, quality)), 4)

    # Estimate demographics based on profile signals
    # (real implementation would use audience data APIs)
    demographics: dict = {
        "estimated_real_followers_pct": round((1 - fraud_score) * 100, 1),
        "engagement_quality": (
            "high" if engagement_rate >= 0.05
            else "medium" if engagement_rate >= 0.02
            else "low"
        ),
        "follower_tier": _classify_follower_tier(followers),
    }

    return {"audience_quality_score": quality, "audience_demographics": demographics}


def estimate_reach_and_cpm(
    followers: int,
    engagement_rate: float,
    content_quality: float,
) -> dict:
    """Estimate reach and CPM based on follower tier and engagement.

    Returns:
        {estimated_reach: int, estimated_cpm: float}
    """
    if followers == 0:
        return {"estimated_reach": 0, "estimated_cpm": 0.0}

    tier = _classify_follower_tier(followers)

    # Base reach multiplier by tier
    tier_reach_multipliers = {
        "nano": 0.25,       # 1K-10K: high reach %
        "micro": 0.15,      # 10K-50K
        "mid": 0.08,        # 50K-500K
        "macro": 0.04,      # 500K+
    }
    base_reach_pct = tier_reach_multipliers.get(tier, 0.10)

    # Adjust reach by engagement (better engagement = higher reach)
    engagement_boost = 1.0 + min(engagement_rate * 10, 1.0)
    estimated_reach = int(followers * base_reach_pct * engagement_boost)

    # Base CPM by tier (EUR)
    tier_base_cpm = {
        "nano": 5.0,
        "micro": 8.0,
        "mid": 12.0,
        "macro": 18.0,
    }
    base_cpm = tier_base_cpm.get(tier, 10.0)

    # Adjust CPM by engagement and content quality
    quality_mult = 0.7 + content_quality * 0.6  # range: 0.7 - 1.3
    engagement_mult = 0.8 + min(engagement_rate * 8, 0.8)  # range: 0.8 - 1.6
    estimated_cpm = round(base_cpm * quality_mult * engagement_mult, 2)

    return {"estimated_reach": estimated_reach, "estimated_cpm": estimated_cpm}


def estimate_audience_overlap(
    profile_a: InfluencerProfileResult,
    profile_b: InfluencerProfileResult,
) -> dict:
    """Estimate audience overlap between two influencers using heuristics.

    Returns:
        {overlap_percentage: float 5-45, sample_size: int}

    Uses hashtag Jaccard similarity + follower size proximity + discovery source bonus.
    """
    # Collect all hashtags from recent posts
    hashtags_a = set()
    for p in profile_a.recent_posts:
        hashtags_a.update(p.hashtags)

    hashtags_b = set()
    for p in profile_b.recent_posts:
        hashtags_b.update(p.hashtags)

    # Jaccard similarity of hashtag sets
    if hashtags_a and hashtags_b:
        intersection = hashtags_a & hashtags_b
        union = hashtags_a | hashtags_b
        jaccard = len(intersection) / len(union)
    else:
        jaccard = 0.0

    # Follower size proximity — similar-sized accounts have more overlap
    followers_a = profile_a.followers_count or 0
    followers_b = profile_b.followers_count or 0
    if followers_a > 0 and followers_b > 0:
        ratio = min(followers_a, followers_b) / max(followers_a, followers_b)
        size_similarity = ratio  # 0-1
    else:
        size_similarity = 0.0

    # Weighted combination → base overlap percentage
    # Jaccard weighted heavily since shared hashtags = shared audience
    base_overlap = jaccard * 0.6 + size_similarity * 0.4

    # Scale to 5-45% range
    overlap_pct = round(5 + base_overlap * 40, 1)
    overlap_pct = max(5.0, min(45.0, overlap_pct))

    sample_size = min(followers_a, followers_b, 10_000)

    return {"overlap_percentage": overlap_pct, "sample_size": max(sample_size, 100)}


def calculate_health_score(influencer_scores: list[dict]) -> float:
    """Calculate overall brand health score from influencer metrics.

    Args:
        influencer_scores: list of dicts, each with keys:
            fraud_score, content_quality_score, audience_quality_score, engagement_rate

    Returns:
        float 0-100

    Weighted composite:
        (1 - fraud) * 0.30 + content * 0.25 + audience * 0.25 + engagement * 0.20
    """
    if not influencer_scores:
        return 0.0

    total = 0.0
    for scores in influencer_scores:
        fraud = scores.get("fraud_score", 0.5)
        content = scores.get("content_quality_score", 0.0)
        audience = scores.get("audience_quality_score", 0.0)
        engagement = scores.get("engagement_rate", 0.0)

        # Normalize engagement to 0-1 (cap at 10%)
        normalized_engagement = min(engagement / 0.10, 1.0)

        individual = (
            (1 - fraud) * 0.30
            + content * 0.25
            + audience * 0.25
            + normalized_engagement * 0.20
        )
        total += individual

    avg = total / len(influencer_scores)
    return round(avg * 100, 1)


def _classify_follower_tier(followers: int) -> str:
    """Classify by follower count into nano/micro/mid/macro."""
    if followers < 10_000:
        return "nano"
    elif followers < 50_000:
        return "micro"
    elif followers < 500_000:
        return "mid"
    else:
        return "macro"
