from __future__ import annotations

import pytest

from app.data_sources.instagram import InstagramDataSource
from app.data_sources.mock_data import (
    generate_mock_brand_profile,
    generate_mock_discovered_influencers,
)
from app.data_sources.schemas import (
    BrandProfileResult,
    DiscoveredInfluencer,
    InfluencerDiscoveryResult,
)


# --- Schema tests ---


class TestBrandProfileResult:
    def test_defaults(self):
        profile = BrandProfileResult(username="test")
        assert profile.username == "test"
        assert profile.followers_count is None
        assert profile.is_verified is False
        assert profile.is_business is False
        assert profile.raw_data == {}

    def test_full_profile(self):
        profile = BrandProfileResult(
            username="nike",
            full_name="Nike",
            biography="Just do it.",
            followers_count=300_000_000,
            is_verified=True,
            is_business=True,
            raw_data={"source": "apify"},
        )
        assert profile.followers_count == 300_000_000
        assert profile.is_verified is True
        assert profile.raw_data["source"] == "apify"


class TestDiscoveredInfluencer:
    def test_defaults(self):
        inf = DiscoveredInfluencer(username="creator1")
        assert inf.discovery_source == "tagged_posts"
        assert inf.discovery_context == ""
        assert inf.followers_count is None


class TestInfluencerDiscoveryResult:
    def test_defaults(self):
        result = InfluencerDiscoveryResult()
        assert result.influencers == []
        assert result.sources_attempted == []
        assert result.errors == []


# --- Mock data tests ---


class TestMockBrandProfile:
    def test_deterministic(self):
        """Same handle always produces the same profile."""
        p1 = generate_mock_brand_profile("nike")
        p2 = generate_mock_brand_profile("nike")
        assert p1.followers_count == p2.followers_count
        assert p1.biography == p2.biography
        assert p1.profile_pic_url == p2.profile_pic_url

    def test_different_handles_produce_different_results(self):
        p1 = generate_mock_brand_profile("nike")
        p2 = generate_mock_brand_profile("adidas")
        # Extremely unlikely to be identical with different seeds
        assert p1.followers_count != p2.followers_count or p1.biography != p2.biography

    def test_followers_in_range(self):
        profile = generate_mock_brand_profile("testbrand")
        assert 5_000 <= profile.followers_count <= 500_000

    def test_is_business(self):
        profile = generate_mock_brand_profile("testbrand")
        assert profile.is_business is True

    def test_has_raw_data(self):
        profile = generate_mock_brand_profile("nike")
        assert profile.raw_data["source"] == "mock"
        assert profile.raw_data["handle"] == "nike"


class TestMockDiscoveredInfluencers:
    def test_deterministic(self):
        r1 = generate_mock_discovered_influencers("nike")
        r2 = generate_mock_discovered_influencers("nike")
        assert len(r1.influencers) == len(r2.influencers)
        assert [i.username for i in r1.influencers] == [
            i.username for i in r2.influencers
        ]

    def test_count_in_range(self):
        result = generate_mock_discovered_influencers("testbrand")
        assert 8 <= len(result.influencers) <= 15

    def test_all_sources_represented(self):
        result = generate_mock_discovered_influencers("testbrand")
        sources = {inf.discovery_source for inf in result.influencers}
        assert "tagged_posts" in sources
        assert "related_profiles" in sources
        assert "hashtag_search" in sources

    def test_no_duplicates(self):
        result = generate_mock_discovered_influencers("testbrand")
        usernames = [inf.username for inf in result.influencers]
        assert len(usernames) == len(set(usernames))

    def test_brand_not_in_results(self):
        """Brand handle should never appear in discovered influencers."""
        # Use a handle that matches one from the pool to test exclusion
        result = generate_mock_discovered_influencers("lifestyle.anna")
        usernames = [inf.username for inf in result.influencers]
        assert "lifestyle.anna" not in usernames

    def test_all_sources_succeeded(self):
        result = generate_mock_discovered_influencers("nike")
        assert result.sources_succeeded == [
            "tagged_posts", "related_profiles", "hashtag_search"
        ]
        assert result.sources_failed == []
        assert result.errors == []


# --- InstagramDataSource tests ---


class TestInstagramDataSource:
    def test_mock_mode_when_no_api_key(self, monkeypatch):
        monkeypatch.setattr("app.config.settings.APIFY_API_KEY", "")
        ds = InstagramDataSource()
        assert ds.is_mock_mode is True

    def test_live_mode_when_api_key_set(self, monkeypatch):
        monkeypatch.setattr("app.config.settings.APIFY_API_KEY", "apify_test_12345")
        ds = InstagramDataSource()
        assert ds.is_mock_mode is False

    @pytest.mark.asyncio
    async def test_scrape_brand_mock(self, monkeypatch):
        monkeypatch.setattr("app.config.settings.APIFY_API_KEY", "")
        ds = InstagramDataSource()
        profile = await ds.scrape_brand_profile("nike")
        assert isinstance(profile, BrandProfileResult)
        assert profile.username == "nike"
        assert profile.followers_count is not None
        assert profile.is_business is True

    @pytest.mark.asyncio
    async def test_discover_influencers_mock(self, monkeypatch):
        monkeypatch.setattr("app.config.settings.APIFY_API_KEY", "")
        ds = InstagramDataSource()
        result = await ds.discover_influencers("nike", "Just do it. #sport #fitness")
        assert isinstance(result, InfluencerDiscoveryResult)
        assert 8 <= len(result.influencers) <= 15
        # Brand should be excluded
        assert all(inf.username != "nike" for inf in result.influencers)


# --- Profile parsing tests ---


class TestProfileParsing:
    def test_parse_profile(self):
        raw = {
            "username": "nike",
            "fullName": "Nike",
            "biography": "Just do it.",
            "followersCount": 300_000_000,
            "followingCount": 200,
            "postsCount": 5000,
            "profilePicUrl": "https://example.com/pic.jpg",
            "verified": True,
            "isBusinessAccount": True,
        }
        result = InstagramDataSource._parse_profile(raw)
        assert result.username == "nike"
        assert result.full_name == "Nike"
        assert result.biography == "Just do it."
        assert result.followers_count == 300_000_000
        assert result.is_verified is True
        assert result.is_business is True
        assert result.raw_data == raw

    def test_parse_profile_missing_fields(self):
        raw = {"username": "minimal"}
        result = InstagramDataSource._parse_profile(raw)
        assert result.username == "minimal"
        assert result.full_name is None
        assert result.followers_count is None
        assert result.is_verified is False

    def test_parse_profile_hd_pic_fallback(self):
        raw = {"username": "test", "profilePicUrlHD": "https://example.com/hd.jpg"}
        result = InstagramDataSource._parse_profile(raw)
        assert result.profile_pic_url == "https://example.com/hd.jpg"


# --- Hashtag extraction tests ---


class TestHashtagExtraction:
    def test_extract_from_handle(self):
        hashtags = InstagramDataSource._extract_hashtags("nike.poland", None)
        assert "nike" in hashtags
        assert "poland" in hashtags

    def test_extract_from_bio(self):
        hashtags = InstagramDataSource._extract_hashtags(
            "brand", "We love #fitness and #health"
        )
        assert "fitness" in hashtags
        assert "health" in hashtags

    def test_combined_handle_and_bio(self):
        hashtags = InstagramDataSource._extract_hashtags(
            "sport.brand", "Follow us! #training"
        )
        assert "sport" in hashtags
        assert "brand" in hashtags
        assert "training" in hashtags

    def test_deduplication(self):
        hashtags = InstagramDataSource._extract_hashtags(
            "nike", "#nike is great"
        )
        assert hashtags.count("nike") == 1

    def test_max_5_hashtags(self):
        hashtags = InstagramDataSource._extract_hashtags(
            "a.b.c",
            "#one #two #three #four #five #six #seven",
        )
        assert len(hashtags) <= 5

    def test_short_parts_excluded(self):
        """Handle parts <= 2 chars should be excluded."""
        hashtags = InstagramDataSource._extract_hashtags("ab.testing", None)
        assert "ab" not in hashtags
        assert "testing" in hashtags

    def test_empty_bio(self):
        hashtags = InstagramDataSource._extract_hashtags("nike", None)
        assert hashtags == ["nike"]

    def test_no_hashtags_possible(self):
        hashtags = InstagramDataSource._extract_hashtags("ab", None)
        assert hashtags == []
