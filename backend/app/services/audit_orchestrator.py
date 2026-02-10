from __future__ import annotations

import itertools
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.data_sources.instagram import InstagramDataSource
from app.data_sources.schemas import InfluencerProfileResult
from app.models.audit import Audit
from app.models.audience_overlap import AudienceOverlap
from app.models.audit_influencer import AuditInfluencer
from app.models.brand import Brand
from app.models.influencer import Influencer
from app.services.scoring import (
    calculate_audience_quality,
    calculate_content_quality,
    calculate_engagement_metrics,
    calculate_fraud_score,
    calculate_health_score,
    estimate_audience_overlap,
    estimate_reach_and_cpm,
)

logger = logging.getLogger(__name__)

PIPELINE_STEPS = [
    ("scraping_brand", "Scraping brand profile", 15),
    ("discovering_influencers", "Discovering associated influencers", 30),
    ("analyzing_influencers", "Analyzing influencer profiles", 55),
    ("scoring", "Calculating scores and metrics", 75),
    ("generating_narrative", "Generating audit narrative", 90),
    ("completed", "Audit complete", 100),
]


class AuditOrchestrator:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.instagram = InstagramDataSource()
        self._profiles: dict[str, InfluencerProfileResult] = {}

    async def run_audit(self, audit_id: str) -> None:
        try:
            for status, step_label, progress in PIPELINE_STEPS:
                await self._update_status(audit_id, status, progress, step_label)

                if status == "scraping_brand":
                    await self._scrape_brand(audit_id)
                elif status == "discovering_influencers":
                    await self._discover_influencers(audit_id)
                elif status == "analyzing_influencers":
                    await self._analyze_influencers(audit_id)
                elif status == "scoring":
                    await self._calculate_scores(audit_id)
                elif status == "generating_narrative":
                    await self._generate_narrative(audit_id)

            logger.info("Audit %s completed successfully", audit_id)

        except Exception as exc:
            logger.exception("Audit %s failed: %s", audit_id, exc)
            await self._update_status(
                audit_id,
                "failed",
                progress=0,
                current_step=None,
                error_message=str(exc),
            )

    async def _update_status(
        self,
        audit_id: str,
        status: str,
        progress: int,
        current_step: str | None,
        error_message: str | None = None,
    ) -> None:
        audit = await self._get_audit(audit_id)
        audit.status = status
        audit.progress = progress
        audit.current_step = current_step
        if error_message is not None:
            audit.error_message = error_message
        await self.db.commit()

    async def _scrape_brand(self, audit_id: str) -> None:
        """Step 1: Scrape brand Instagram profile and update the Brand row."""
        audit = await self._get_audit(audit_id)
        brand = await self._get_brand(audit.brand_id)

        logger.info("Step 1 - Scraping brand profile for @%s", brand.instagram_handle)

        profile = await self.instagram.scrape_brand_profile(brand.instagram_handle)

        brand.followers_count = profile.followers_count
        brand.bio = profile.biography
        brand.profile_pic_url = profile.profile_pic_url
        brand.profile_data = profile.raw_data
        brand.last_scraped_at = datetime.now(timezone.utc)

        await self.db.commit()

        logger.info(
            "Brand @%s scraped: %s followers",
            brand.instagram_handle,
            profile.followers_count,
        )

    async def _discover_influencers(self, audit_id: str) -> None:
        """Step 2: Discover influencers and create DB records."""
        audit = await self._get_audit(audit_id)
        brand = await self._get_brand(audit.brand_id)

        logger.info(
            "Step 2 - Discovering influencers for @%s", brand.instagram_handle
        )

        discovery = await self.instagram.discover_influencers(
            brand.instagram_handle, brand.bio
        )

        logger.info(
            "Found %d influencers for @%s (succeeded: %s, failed: %s)",
            len(discovery.influencers),
            brand.instagram_handle,
            discovery.sources_succeeded,
            discovery.sources_failed,
        )

        # Batch-fetch existing influencers to avoid N+1 queries
        usernames = [d.username for d in discovery.influencers]
        result = await self.db.execute(
            select(Influencer).where(Influencer.instagram_handle.in_(usernames))
        )
        existing = {inf.instagram_handle: inf for inf in result.scalars()}

        for discovered in discovery.influencers:
            influencer = existing.get(discovered.username)

            if influencer is None:
                influencer = Influencer(
                    instagram_handle=discovered.username,
                    followers_count=discovered.followers_count,
                )
                self.db.add(influencer)
                await self.db.flush()
                existing[discovered.username] = influencer

            # Create AuditInfluencer junction record
            audit_influencer = AuditInfluencer(
                audit_id=audit_id,
                influencer_id=influencer.id,
                discovery_source=discovered.discovery_source,
            )
            self.db.add(audit_influencer)

        await self.db.commit()

        logger.info(
            "Created %d audit-influencer records for audit %s",
            len(discovery.influencers),
            audit_id,
        )

    async def _analyze_influencers(self, audit_id: str) -> None:
        """Step 3: Scrape full profiles and calculate engagement metrics."""
        logger.info("Step 3 - Analyzing influencers for audit %s", audit_id)

        # Fetch all AuditInfluencer rows with joined Influencer
        result = await self.db.execute(
            select(AuditInfluencer)
            .options(selectinload(AuditInfluencer.influencer))
            .where(AuditInfluencer.audit_id == audit_id)
        )
        audit_influencers = list(result.scalars())

        for ai in audit_influencers:
            influencer = ai.influencer
            handle = influencer.instagram_handle

            # Scrape full profile
            profile = await self.instagram.scrape_influencer_profile(handle)
            self._profiles[handle] = profile

            # Update Influencer row with scraped data
            influencer.display_name = profile.full_name
            influencer.followers_count = profile.followers_count
            influencer.following_count = profile.following_count
            influencer.posts_count = profile.posts_count
            influencer.bio = profile.biography
            influencer.profile_pic_url = profile.profile_pic_url
            influencer.profile_data = profile.raw_data
            influencer.last_scraped_at = datetime.now(timezone.utc)

            # Calculate engagement metrics
            metrics = calculate_engagement_metrics(profile)
            ai.engagement_rate = metrics["engagement_rate"]
            ai.avg_likes = metrics["avg_likes"]
            ai.avg_comments = metrics["avg_comments"]

        await self.db.commit()
        logger.info(
            "Analyzed %d influencers for audit %s", len(audit_influencers), audit_id
        )

    async def _calculate_scores(self, audit_id: str) -> None:
        """Step 4: Run fraud, content, audience, reach/CPM scoring + overlap + health."""
        logger.info("Step 4 - Calculating scores for audit %s", audit_id)

        result = await self.db.execute(
            select(AuditInfluencer)
            .options(selectinload(AuditInfluencer.influencer))
            .where(AuditInfluencer.audit_id == audit_id)
        )
        audit_influencers = list(result.scalars())

        health_inputs: list[dict] = []

        for ai in audit_influencers:
            handle = ai.influencer.instagram_handle
            profile = self._profiles.get(handle)

            if profile is None:
                logger.warning("No cached profile for @%s, skipping scoring", handle)
                continue

            engagement_rate = ai.engagement_rate or 0.0
            avg_likes = ai.avg_likes or 0.0
            avg_comments = ai.avg_comments or 0.0

            # Fraud scoring
            fraud = calculate_fraud_score(profile, engagement_rate, avg_likes, avg_comments)
            ai.fraud_score = fraud["fraud_score"]
            ai.fraud_indicators = fraud["fraud_indicators"]

            # Content quality
            content = calculate_content_quality(profile)
            ai.content_quality_score = content["content_quality_score"]
            ai.content_analysis = content["content_analysis"]

            # Audience quality
            audience = calculate_audience_quality(profile, engagement_rate, fraud["fraud_score"])
            ai.audience_quality_score = audience["audience_quality_score"]
            ai.audience_demographics = audience["audience_demographics"]

            # Reach & CPM
            reach = estimate_reach_and_cpm(
                profile.followers_count or 0,
                engagement_rate,
                content["content_quality_score"],
            )
            ai.estimated_reach = reach["estimated_reach"]
            ai.estimated_cpm = reach["estimated_cpm"]

            health_inputs.append({
                "fraud_score": fraud["fraud_score"],
                "content_quality_score": content["content_quality_score"],
                "audience_quality_score": audience["audience_quality_score"],
                "engagement_rate": engagement_rate,
            })

        # Pairwise audience overlap
        handles_and_ids = [
            (ai.influencer.instagram_handle, ai.influencer_id)
            for ai in audit_influencers
            if ai.influencer.instagram_handle in self._profiles
        ]

        for (handle_a, id_a), (handle_b, id_b) in itertools.combinations(handles_and_ids, 2):
            profile_a = self._profiles[handle_a]
            profile_b = self._profiles[handle_b]
            overlap = estimate_audience_overlap(profile_a, profile_b)

            self.db.add(AudienceOverlap(
                audit_id=audit_id,
                influencer_a_id=id_a,
                influencer_b_id=id_b,
                overlap_percentage=overlap["overlap_percentage"],
                sample_size=overlap["sample_size"],
            ))

        # Health score
        audit = await self._get_audit(audit_id)
        audit.health_score = calculate_health_score(health_inputs)

        await self.db.commit()

        # Clean up cached profiles
        self._profiles.clear()

        logger.info("Scoring complete for audit %s (health=%.1f)", audit_id, audit.health_score)

    async def _generate_narrative(self, audit_id: str) -> None:
        """Step 5: Generate executive summary and recommendations via LLM. Stubbed."""
        logger.info("Step 5 - Generating narrative for audit %s (stub)", audit_id)

    # --- Helpers ---

    async def _get_audit(self, audit_id: str) -> Audit:
        result = await self.db.execute(select(Audit).where(Audit.id == audit_id))
        return result.scalar_one()

    async def _get_brand(self, brand_id: str) -> Brand:
        result = await self.db.execute(select(Brand).where(Brand.id == brand_id))
        return result.scalar_one()
