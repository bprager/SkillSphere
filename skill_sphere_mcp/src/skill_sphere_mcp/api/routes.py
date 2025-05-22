"""API route definitions and handlers."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.db.neo4j import neo4j_conn

logger = logging.getLogger(__name__)
router = APIRouter()

get_db_session = Depends(neo4j_conn.get_session)


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/skills")
async def get_skills(
    session: AsyncSession = get_db_session,
) -> list[dict[str, str]]:
    """Get all skills from the database."""
    try:
        result = await session.run("MATCH (s:Skill) RETURN s.name as name")
        skills = [{"name": record["name"]} async for record in result]
        return skills
    except Exception as exc:
        logger.error("Failed to fetch skills: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch skills") from exc


@router.post("/skills")
async def create_skill(
    name: str, session: AsyncSession = get_db_session
) -> dict[str, str]:
    """Create a new skill in the database."""
    try:
        result = await session.run(
            "CREATE (s:Skill {name: $name}) RETURN s.name as name", name=name
        )
        record = await result.single()
        if not record:
            raise HTTPException(status_code=500, detail="Failed to create skill")
        return {"name": record["name"]}
    except Exception as exc:
        logger.error("Failed to create skill: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create skill") from exc
