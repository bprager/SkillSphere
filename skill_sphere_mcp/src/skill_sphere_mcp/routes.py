"""Main API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession

from .api.routes import router as api_router
from .db.deps import get_db_session

logger = logging.getLogger(__name__)

router = APIRouter()

# Include the API router
router.include_router(api_router, prefix="/api", tags=["api"])


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "SkillSphere MCP Server"}


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/db-test")
async def test_db_connection(session: AsyncSession = Depends(get_db_session)) -> dict[str, str]:
    """Test database connection."""
    try:
        result = await session.run("RETURN 1 as test")
        record = await result.single()
        if record and record["test"] == 1:
            return {"status": "Database connection successful"}
        raise HTTPException(status_code=500, detail="Database test failed")
    except Exception as e:
        logger.error("Database test failed: %s", e)
        raise HTTPException(status_code=500, detail="Database connection failed") from e
