from __future__ import annotations

import logging
import re

from app.config import settings
from app.data_sources.mock_data import (
    generate_mock_brand_profile,
    generate_mock_discovered_influencers,
    generate_mock_influencer_profile,
)
from app.data_sources.schemas import (
    BrandProfileResult,
    DiscoveredInfluencer,
    InfluencerDiscoveryResult,
    InfluencerProfileResult,
    PostData,
)

logger = logging.getLogger(__name__)

# Apify actor IDs
_PROFILE_SCRAPER = "apify/instagram-profile-scraper"
_TAGGED_SCRAPER = "apify/instagram-tag-scraper"
_HASHTAG_SCRAPER = "apify/instagram-hashtag-scraper"

# Limits to control Apify costs
_TAGGED_RESULTS_LIMIT = 50
_HASHTAG_RESULTS_LIMIT = 30
_MAX_HASHTAGS = 5
_ACTOR_TIMEOUT_SECS = 180


class InstagramDataSource:
    """Instagram data source backed by Apify actors, with mock mode fallback."""

    @property
    def is_mock_mode(self) -> bool:
        return not settings.APIFY_API_KEY

    async def scrape_brand_profile(self, handle: str) -> BrandProfileResult:
        """Scrape an Instagram brand profile. Falls back to mock in dev."""
        if self.is_mock_mode:
            logger.info("Mock mode: generating brand profile for @%s", handle)
            return generate_mock_brand_profile(handle)

        logger.info("Scraping brand profile for @%s via Apify", handle)
        return await self._scrape_profile_via_apify(handle)

    async def scrape_influencer_profile(self, handle: str) -> InfluencerProfileResult:
        """Scrape a full influencer profile with recent posts. Falls back to mock in dev."""
        if self.is_mock_mode:
            logger.info("Mock mode: generating influencer profile for @%s", handle)
            return generate_mock_influencer_profile(handle)

        logger.info("Scraping influencer profile for @%s via Apify", handle)
        return await self._scrape_influencer_via_apify(handle)

    async def discover_influencers(
        self, brand_handle: str, brand_bio: str | None = None
    ) -> InfluencerDiscoveryResult:
        """Discover influencers via tagged posts, related profiles, and hashtags.

        Continues on partial failure — if one method fails, the others still run.
        """
        if self.is_mock_mode:
            logger.info("Mock mode: generating discovered influencers for @%s", brand_handle)
            return generate_mock_discovered_influencers(brand_handle)

        logger.info("Discovering influencers for @%s via Apify", brand_handle)

        result = InfluencerDiscoveryResult()
        seen_usernames: set[str] = set()

        discovery_methods = [
            ("tagged_posts", self._discover_from_tagged_posts, (brand_handle,)),
            ("related_profiles", self._discover_from_related_profiles, (brand_handle,)),
            ("hashtag_search", self._discover_from_hashtags, (brand_handle, brand_bio)),
        ]

        for source_name, method, args in discovery_methods:
            result.sources_attempted.append(source_name)
            try:
                found = await method(*args)
                result.sources_succeeded.append(source_name)

                for inf in found:
                    if inf.username == brand_handle:
                        continue
                    if inf.username in seen_usernames:
                        continue
                    seen_usernames.add(inf.username)
                    result.influencers.append(inf)

            except Exception as exc:
                logger.warning(
                    "Discovery method %s failed for @%s: %s",
                    source_name, brand_handle, exc,
                )
                result.sources_failed.append(source_name)
                result.errors.append(f"{source_name}: {exc}")

        logger.info(
            "Discovered %d unique influencers for @%s (succeeded: %s, failed: %s)",
            len(result.influencers),
            brand_handle,
            result.sources_succeeded,
            result.sources_failed,
        )
        return result

    # --- Apify integration methods ---

    async def _scrape_profile_via_apify(self, handle: str) -> BrandProfileResult:
        """Call Apify Instagram profile scraper and parse the result."""
        from apify_client import ApifyClientAsync

        client = ApifyClientAsync(token=settings.APIFY_API_KEY)
        run_input = {
            "usernames": [handle],
            "resultsLimit": 1,
        }

        run = await client.actor(_PROFILE_SCRAPER).call(
            run_input=run_input,
            timeout_secs=_ACTOR_TIMEOUT_SECS,
        )
        items = []
        async for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)

        if not items:
            raise ValueError(f"No profile data returned for @{handle}")

        return self._parse_profile(items[0])

    async def _discover_from_tagged_posts(
        self, brand_handle: str
    ) -> list[DiscoveredInfluencer]:
        """Find influencers who tagged the brand in their posts."""
        from apify_client import ApifyClientAsync

        client = ApifyClientAsync(token=settings.APIFY_API_KEY)
        run_input = {
            "username": brand_handle,
            "resultsLimit": _TAGGED_RESULTS_LIMIT,
        }

        run = await client.actor(_TAGGED_SCRAPER).call(
            run_input=run_input,
            timeout_secs=_ACTOR_TIMEOUT_SECS,
        )

        influencers = []
        seen = set()
        async for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            owner = item.get("ownerUsername") or item.get("owner", {}).get("username")
            if not owner or owner in seen:
                continue
            seen.add(owner)
            influencers.append(
                DiscoveredInfluencer(
                    username=owner,
                    followers_count=item.get("ownerFollowers"),
                    discovery_source="tagged_posts",
                    discovery_context=f"Tagged @{brand_handle} in post",
                )
            )

        return influencers

    async def _discover_from_related_profiles(
        self, brand_handle: str
    ) -> list[DiscoveredInfluencer]:
        """Get related/suggested profiles from the brand's profile page."""
        from apify_client import ApifyClientAsync

        client = ApifyClientAsync(token=settings.APIFY_API_KEY)
        run_input = {
            "usernames": [brand_handle],
            "resultsLimit": 1,
        }

        run = await client.actor(_PROFILE_SCRAPER).call(
            run_input=run_input,
            timeout_secs=_ACTOR_TIMEOUT_SECS,
        )

        influencers = []
        async for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            for related in item.get("relatedProfiles", []):
                username = related.get("username")
                if not username:
                    continue
                influencers.append(
                    DiscoveredInfluencer(
                        username=username,
                        followers_count=related.get("followersCount"),
                        discovery_source="related_profiles",
                        discovery_context=f"Suggested profile from @{brand_handle}",
                    )
                )

        return influencers

    async def _discover_from_hashtags(
        self, brand_handle: str, brand_bio: str | None
    ) -> list[DiscoveredInfluencer]:
        """Extract hashtags from handle + bio, search for top posters."""
        hashtags = self._extract_hashtags(brand_handle, brand_bio)
        if not hashtags:
            return []

        from apify_client import ApifyClientAsync

        client = ApifyClientAsync(token=settings.APIFY_API_KEY)

        influencers = []
        seen = set()

        for hashtag in hashtags[:_MAX_HASHTAGS]:
            run_input = {
                "hashtags": [hashtag],
                "resultsLimit": _HASHTAG_RESULTS_LIMIT,
            }

            try:
                run = await client.actor(_HASHTAG_SCRAPER).call(
                    run_input=run_input,
                    timeout_secs=_ACTOR_TIMEOUT_SECS,
                )

                async for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    owner = item.get("ownerUsername") or item.get("owner", {}).get("username")
                    if not owner or owner in seen:
                        continue
                    seen.add(owner)
                    influencers.append(
                        DiscoveredInfluencer(
                            username=owner,
                            followers_count=item.get("ownerFollowers"),
                            discovery_source="hashtag_search",
                            discovery_context=f"Found via #{hashtag}",
                        )
                    )
            except Exception as exc:
                logger.warning("Hashtag search for #%s failed: %s", hashtag, exc)

        return influencers

    async def _scrape_influencer_via_apify(self, handle: str) -> InfluencerProfileResult:
        """Call Apify Instagram profile scraper with posts and parse the result."""
        from apify_client import ApifyClientAsync

        client = ApifyClientAsync(token=settings.APIFY_API_KEY)
        run_input = {
            "usernames": [handle],
            "resultsLimit": 20,
        }

        run = await client.actor(_PROFILE_SCRAPER).call(
            run_input=run_input,
            timeout_secs=_ACTOR_TIMEOUT_SECS,
        )
        items = []
        async for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)

        if not items:
            raise ValueError(f"No profile data returned for @{handle}")

        return self._parse_influencer_profile(items[0])

    @staticmethod
    def _parse_influencer_profile(data: dict) -> InfluencerProfileResult:
        """Parse Apify profile scraper output into InfluencerProfileResult."""
        from datetime import datetime

        recent_posts: list[PostData] = []
        for post in data.get("latestPosts", []):
            post_type_raw = post.get("type", "Image")
            type_map = {
                "Image": "image",
                "Video": "video",
                "Carousel": "carousel",
                "Reel": "reel",
            }
            post_type = type_map.get(post_type_raw, "image")

            caption = post.get("caption", "") or ""
            hashtags = re.findall(r"#(\w+)", caption)

            timestamp = None
            ts_raw = post.get("timestamp")
            if ts_raw:
                try:
                    timestamp = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            recent_posts.append(PostData(
                post_id=post.get("id", post.get("shortCode", "")),
                post_type=post_type,
                caption=caption,
                likes_count=post.get("likesCount", 0),
                comments_count=post.get("commentsCount", 0),
                timestamp=timestamp,
                hashtags=hashtags,
            ))

        return InfluencerProfileResult(
            username=data.get("username", ""),
            full_name=data.get("fullName"),
            biography=data.get("biography"),
            followers_count=data.get("followersCount"),
            following_count=data.get("followingCount"),
            posts_count=data.get("postsCount"),
            profile_pic_url=data.get("profilePicUrl") or data.get("profilePicUrlHD"),
            is_verified=bool(data.get("verified", False)),
            recent_posts=recent_posts,
            raw_data=data,
        )

    # --- Helpers ---

    @staticmethod
    def _parse_profile(data: dict) -> BrandProfileResult:
        """Parse Apify profile scraper output into our DTO."""
        return BrandProfileResult(
            username=data.get("username", ""),
            full_name=data.get("fullName"),
            biography=data.get("biography"),
            followers_count=data.get("followersCount"),
            following_count=data.get("followingCount"),
            posts_count=data.get("postsCount"),
            profile_pic_url=data.get("profilePicUrl") or data.get("profilePicUrlHD"),
            is_verified=bool(data.get("verified", False)),
            is_business=bool(data.get("isBusinessAccount", False)),
            raw_data=data,
        )

    @staticmethod
    def _extract_hashtags(handle: str, bio: str | None) -> list[str]:
        """Extract hashtags from handle parts and bio text."""
        hashtags: list[str] = []

        # Split handle into words (e.g., "nike.poland" → ["nike", "poland"])
        parts = re.split(r"[._]", handle)
        hashtags.extend(p.lower() for p in parts if len(p) > 2)

        # Extract #hashtags from bio
        if bio:
            found = re.findall(r"#(\w+)", bio)
            hashtags.extend(h.lower() for h in found)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for h in hashtags:
            if h not in seen:
                seen.add(h)
                unique.append(h)

        return unique[:_MAX_HASHTAGS]
