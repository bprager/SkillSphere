"""Database utility functions."""

import logging

from typing import Any

from fastapi import HTTPException
from neo4j import AsyncSession


logger = logging.getLogger(__name__)

async def get_entity_by_id(session: AsyncSession, entity_id: str) -> dict[str, Any]:
    """Get an entity by ID from the database.

    Args:
        session: Neo4j database session
        entity_id: ID of the entity to retrieve

    Returns:
        Entity data as a dictionary including relationships

    Raises:
        HTTPException: If entity is not found or ID is invalid
    """
    if not entity_id or not isinstance(entity_id, str):
        raise HTTPException(
            status_code=400,
            detail="Invalid entity ID. Must be a non-empty string.",
        )

    # Query to get the node and its relationships
    query = """
    MATCH (n) WHERE n.id = $id
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n,
           labels(n) as labels,
           collect({
               type: type(r),
               target: m,
               target_labels: labels(m)
           }) as relationships
    """

    try:
        result = await session.run(query, {"id": entity_id})
        record = await result.single()

        if not record:
            raise HTTPException(status_code=404, detail="Entity not found")

        node = record["n"]
        labels = record["labels"]
        relationships = record["relationships"]

        # Convert Neo4j node to dictionary
        entity_data = dict(node)

        # Add metadata
        entity_data.update(
            {
                "id": entity_id,
                "type": labels[0] if labels else None,
                "relationships": [
                    {
                        "type": rel["type"],
                        "target": dict(rel["target"]),
                        "target_type": (
                            rel["target_labels"][0] if rel["target_labels"] else None
                        ),
                    }
                    for rel in relationships
                    if rel["type"] is not None  # Filter out null relationships
                ],
            }
        )

        return entity_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_entity_by_id: Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") from e
