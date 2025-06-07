"""Database dependencies."""

from neo4j import AsyncSession

from .connection import neo4j_conn


async def get_db_session() -> AsyncSession:
    """Get a Neo4j database session.

    Returns:
        Neo4j database session
    """
    async for session in neo4j_conn.get_session():
        return session
    raise RuntimeError("Failed to get database session")
