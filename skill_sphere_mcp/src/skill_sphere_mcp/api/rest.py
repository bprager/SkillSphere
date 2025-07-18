"""Legacy REST API routes."""

from fastapi import APIRouter, Depends, HTTPException
from neo4j import AsyncSession

from ..db.deps import get_db_session
from ..db.utils import get_entity_by_id

router = APIRouter()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    """Health check endpoint for infrastructure."""
    return {"status": "ok"}


@router.get("/entity/{entity_id}")
async def get_entity_legacy(
    entity_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get an entity by ID (legacy endpoint)."""
    try:
        entity = await get_entity_by_id(session, entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch entity") from exc


@router.post("/search")
async def search_semantic(
    request: dict,
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """Semantic search endpoint (legacy)."""
    try:
        query = request.get("query", "")
        k = request.get("k", 10)

        # Simple mock implementation for now
        # In a real implementation, this would use embeddings
        result = await session.run(
            "MATCH (n) WHERE n.name CONTAINS $query RETURN n LIMIT $k",
            {"query": query, "k": k},
        )

        records = []
        async for record in result:
            node = record["n"]
            records.append(
                {
                    "entity_id": node.get("id", str(node.get("name", ""))),
                    "score": 0.8,  # Mock score
                }
            )

        return records
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Search failed") from exc
