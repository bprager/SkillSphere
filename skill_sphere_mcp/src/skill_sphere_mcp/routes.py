"""Route handlers for the MCP server."""

import logging

from typing import Any

import numpy as np

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import-untyped]

from .db.connection import neo4j_conn
from .models.embedding import get_embedding_model


logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/v1")

# Get the model instance
MODEL = get_embedding_model()


class Entity(BaseModel):
    """Graph entity with ID, labels, properties and optional relationships."""

    id: str
    labels: list[str]
    properties: dict[str, Any]
    relationships: list[dict[str, Any]] | None = None


class SearchRequest(BaseModel):
    """Search request with query string and optional result limit."""

    query: str
    k: int = 10  # top-k results


class SearchResult(BaseModel):
    """Search result with entity ID and relevance score."""

    entity_id: str
    score: float


@router.get("/healthz", summary="Health check")
async def health_check() -> dict[str, str]:
    """Return service health status."""
    logger.debug("Health check requested")
    return {"status": "ok"}


@router.get("/entity/{entity_id}", response_model=Entity, summary="Get entity by ID")
async def get_entity(entity_id: int) -> Entity:
    """Get a graph entity by its ID, including its relationships."""
    logger.info("Fetching entity with ID: %d", entity_id)
    cypher = (
        "MATCH (n) WHERE id(n) = $id "
        "OPTIONAL MATCH (n)-[r]->(m) "
        "RETURN n, collect({"
        "    relType: type(r), "
        "    targetId: id(m), "
        "    targetLabels: labels(m)"
        "}) AS rels"
    )
    async for ses in neo4j_conn.get_session():
        result = await ses.run(cypher, id=entity_id)
        record = await result.single()
        if not record:
            logger.warning("Entity not found: %d", entity_id)
            raise HTTPException(status_code=404, detail="Entity not found")
        node = record["n"]
        rels = record["rels"]
        logger.debug("Found entity with %d relationships", len(rels))
        return Entity(
            id=str(node.id),
            labels=list(node.labels),
            properties=dict(node),
            relationships=rels,
        )
    raise HTTPException(status_code=500, detail="Database session error")


@router.post(
    "/search", response_model=list[SearchResult], summary="Semantic / graph search"
)
async def search(request: SearchRequest) -> list[SearchResult]:
    """Search for entities using semantic or graph-based queries."""
    logger.info("Search request: %s (k=%d)", request.query, request.k)

    try:
        if MODEL is None:
            raise ImportError("sentence-transformers not available")

        # Encode query
        query_embedding = MODEL.encode(request.query)

        # Get all nodes with their embeddings
        cypher = """
        MATCH (n)
        WHERE n.embedding IS NOT NULL
        RETURN id(n) as id, n.embedding as embedding
        """

        async for ses in neo4j_conn.get_session():
            result = await ses.run(cypher)
            records = [record async for record in result]
            results = []
            for record in records:
                node_id = record["id"]
                node_embedding = np.array(record["embedding"])

                # Compute cosine similarity
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1), node_embedding.reshape(1, -1)
                )[0][0]

                results.append(
                    SearchResult(entity_id=str(node_id), score=float(similarity))
                )

            # Sort by score and return top-k
            results.sort(key=lambda x: x.score, reverse=True)
            return results[: request.k]
        raise HTTPException(status_code=500, detail="Database session error")

    except ImportError as exc:
        logger.error("Semantic search failed: %s", exc)
        raise HTTPException(
            status_code=501,
            detail="Semantic search not available - sentence-transformers not installed",
        ) from exc
    except Exception as exc:
        logger.error("Search failed: %s", exc)
        raise HTTPException(status_code=500, detail="Search operation failed") from exc
