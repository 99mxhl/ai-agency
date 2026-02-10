from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.audit import Audit
from app.models.audit_influencer import AuditInfluencer
from app.models.audience_overlap import AudienceOverlap
from app.models.brand import Brand
from app.models.influencer import Influencer
from app.schemas.audit import (
    AudienceOverlapEntry,
    AuditCreate,
    AuditResult,
    AuditStatus,
    BrandOverview,
    InfluencerAnalysis,
)
from app.workers.audit_worker import run_audit_background

router = APIRouter()


@router.post("/audits", response_model=AuditStatus, status_code=201)
async def create_audit(
    payload: AuditCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> AuditStatus:
    handle = payload.instagram_handle.lower().strip().lstrip("@")

    # Find or create brand
    result = await db.execute(select(Brand).where(Brand.instagram_handle == handle))
    brand = result.scalar_one_or_none()

    if brand is None:
        brand = Brand(instagram_handle=handle)
        db.add(brand)
        await db.flush()

    # Create audit
    audit = Audit(brand_id=brand.id, language=payload.language)
    db.add(audit)
    await db.flush()

    audit_id = audit.id
    created_at = audit.created_at

    # Commit so the background worker can read the audit
    await db.commit()

    # Kick off background processing with its own DB session
    background_tasks.add_task(run_audit_background, audit_id, settings.DATABASE_URL)

    return AuditStatus(
        id=audit_id,
        status="pending",
        progress=0,
        current_step=None,
        created_at=created_at,
    )


@router.get("/audits/lookup", response_model=AuditResult | None)
async def lookup_audit(
    handle: str = Query(..., description="Instagram handle to look up"),
    db: AsyncSession = Depends(get_db),
) -> AuditResult | None:
    clean_handle = handle.lower().strip().lstrip("@")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    result = await db.execute(
        select(Audit)
        .join(Brand)
        .where(Brand.instagram_handle == clean_handle)
        .where(Audit.created_at >= cutoff)
        .order_by(Audit.created_at.desc())
        .limit(1)
    )
    audit = result.scalar_one_or_none()

    if audit is None:
        return None

    return await _build_audit_result(audit, db)


@router.get("/audits/{audit_id}", response_model=AuditResult)
async def get_audit(
    audit_id: str,
    db: AsyncSession = Depends(get_db),
) -> AuditResult:
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()

    if audit is None:
        raise HTTPException(status_code=404, detail="Audit not found")

    return await _build_audit_result(audit, db)


@router.get("/audits/{audit_id}/pdf")
async def get_audit_pdf(audit_id: str) -> None:
    raise HTTPException(status_code=501, detail="PDF generation not yet implemented")


async def _build_audit_result(audit: Audit, db: AsyncSession) -> AuditResult:
    brand = audit.brand

    brand_overview = None
    if brand:
        brand_overview = BrandOverview(
            handle=brand.instagram_handle,
            followers_count=brand.followers_count,
            profile_pic_url=brand.profile_pic_url,
            bio=brand.bio,
        )

    # Fetch influencer analyses
    influencer_rows = await db.execute(
        select(AuditInfluencer, Influencer)
        .join(Influencer, AuditInfluencer.influencer_id == Influencer.id)
        .where(AuditInfluencer.audit_id == audit.id)
    )
    influencers = []
    for ai, inf in influencer_rows:
        influencers.append(
            InfluencerAnalysis(
                handle=inf.instagram_handle,
                display_name=inf.display_name,
                profile_pic_url=inf.profile_pic_url,
                followers_count=inf.followers_count,
                engagement_rate=ai.engagement_rate,
                fraud_score=ai.fraud_score,
                fraud_indicators=ai.fraud_indicators,
                content_quality_score=ai.content_quality_score,
                audience_demographics=ai.audience_demographics,
                audience_quality_score=ai.audience_quality_score,
                estimated_reach=ai.estimated_reach,
                discovery_source=ai.discovery_source,
            )
        )

    # Fetch audience overlaps (relationships use selectin, no N+1)
    overlap_rows = await db.execute(
        select(AudienceOverlap).where(AudienceOverlap.audit_id == audit.id)
    )

    overlaps = []
    for ao in overlap_rows.scalars():
        overlaps.append(
            AudienceOverlapEntry(
                influencer_a_handle=ao.influencer_a.instagram_handle,
                influencer_b_handle=ao.influencer_b.instagram_handle,
                overlap_percentage=ao.overlap_percentage,
            )
        )

    recommendations = audit.recommendations if audit.recommendations else []

    return AuditResult(
        id=audit.id,
        status=audit.status,
        progress=audit.progress,
        current_step=audit.current_step,
        brand=brand_overview,
        health_score=audit.health_score,
        executive_summary=audit.executive_summary,
        recommendations=recommendations,
        influencers=influencers,
        audience_overlaps=overlaps,
        language=audit.language,
        created_at=audit.created_at,
    )
