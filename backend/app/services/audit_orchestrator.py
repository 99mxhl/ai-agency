from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Audit

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
        result = await self.db.execute(select(Audit).where(Audit.id == audit_id))
        audit = result.scalar_one()
        audit.status = status
        audit.progress = progress
        audit.current_step = current_step
        if error_message is not None:
            audit.error_message = error_message
        await self.db.commit()

    async def _scrape_brand(self, audit_id: str) -> None:
        """Step 1: Scrape brand Instagram profile. Stubbed."""
        logger.info("Step 1 - Scraping brand for audit %s (stub)", audit_id)

    async def _discover_influencers(self, audit_id: str) -> None:
        """Step 2: Discover influencers associated with the brand. Stubbed."""
        logger.info("Step 2 - Discovering influencers for audit %s (stub)", audit_id)

    async def _analyze_influencers(self, audit_id: str) -> None:
        """Step 3: Analyze each discovered influencer. Stubbed."""
        logger.info("Step 3 - Analyzing influencers for audit %s (stub)", audit_id)

    async def _calculate_scores(self, audit_id: str) -> None:
        """Step 4: Calculate fraud, quality, and health scores. Stubbed."""
        logger.info("Step 4 - Calculating scores for audit %s (stub)", audit_id)

    async def _generate_narrative(self, audit_id: str) -> None:
        """Step 5: Generate executive summary and recommendations via LLM. Stubbed."""
        logger.info("Step 5 - Generating narrative for audit %s (stub)", audit_id)
