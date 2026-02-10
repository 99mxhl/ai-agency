from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import v1_router
from app.config import settings
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: verify DB connection
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)
    yield
    # Shutdown: dispose engine
    await engine.dispose()


app = FastAPI(
    title="Influencer Marketing Audit API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
