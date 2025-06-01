"""Database utility functions."""

from typing import Any

from fastapi import HTTPException
from neo4j import AsyncSession


async def get_entity_by_id(session: AsyncSession, entity_id: str) -> dict[str, Any]:
    """Get an entity by ID from the database.

    Args:
        session: Neo4j database session
        entity_id: ID of the entity to retrieve

    Returns:
        Entity data as a dictionary

    Raises:
        HTTPException: If entity is not found
    """
    result = await session.run(
        "MATCH (n) WHERE n.id = $id RETURN n",
        {"id": entity_id},
    )
    record = await result.single()
    if not record:
        raise HTTPException(status_code=404, detail="Entity not found")
    return dict(record["n"])
