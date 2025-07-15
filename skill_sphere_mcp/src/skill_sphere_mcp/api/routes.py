"""API route definitions and handlers."""

import logging

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.responses import Response
from neo4j import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import Counter
from prometheus_client import generate_latest

from ..db.deps import get_db_session
from ..db.utils import get_entity_by_id
from ..models.skill import Skill
from .mcp.utils import create_skill_in_db


logger = logging.getLogger(__name__)
router = APIRouter()

# Define a counter metric
request_count = Counter('request_count', 'Total number of requests')


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/skills", response_model=list[Skill])
async def get_skills(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[Skill]:
    """Get all skills from the database."""
    try:
        result = await session.run("MATCH (s:Skill) RETURN s")
        records = await result.fetch_all()  # type: ignore[attr-defined]
        return [Skill(**record["s"]) for record in records]
    except Exception as exc:
        logger.error("Failed to fetch skills: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch skills") from exc


@router.post("/skills", response_model=Skill)
async def create_skill(
    skill: Skill, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> Skill:
    """Create a new skill in the database."""
    return await create_skill_in_db(skill, session)


@router.get("/entities/{entity_id}", response_model=dict)
async def get_entity(
    entity_id: str,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    """Get an entity by ID."""
    try:
        return await get_entity_by_id(session, entity_id)
    except Exception as exc:
        logger.error("Failed to fetch entity: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch entity") from exc


@router.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics."""
    request_count.inc()  # Increment the counter
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
