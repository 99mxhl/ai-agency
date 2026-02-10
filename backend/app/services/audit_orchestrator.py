from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_sources.instagram import InstagramDataSource
from app.models.audit import Audit
from app.models.audit_influencer import AuditInfluencer
from app.models.brand import Brand
from app.models.influencer import Influencer

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
        """Step 3: Analyze each discovered influencer. Stubbed."""
        logger.info("Step 3 - Analyzing influencers for audit %s (stub)", audit_id)

    async def _calculate_scores(self, audit_id: str) -> None:
        """Step 4: Calculate fraud, quality, and health scores. Stubbed."""
        logger.info("Step 4 - Calculating scores for audit %s (stub)", audit_id)

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
