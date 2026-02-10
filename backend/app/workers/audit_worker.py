from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.services.audit_orchestrator import AuditOrchestrator

logger = logging.getLogger(__name__)


async def run_audit_background(audit_id: str, db_url: str) -> None:
    """Run the full audit pipeline in a background task with its own DB session."""
    logger.info("Starting background audit worker for audit %s", audit_id)

    engine = create_async_engine(db_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with session_factory() as session:
            orchestrator = AuditOrchestrator(session)
            await orchestrator.run_audit(audit_id)
    except Exception:
        logger.exception("Background audit worker failed for audit %s", audit_id)
    finally:
        await engine.dispose()
