"""Database dependencies."""

from collections.abc import AsyncGenerator

from neo4j import AsyncSession

from .connection import neo4j_conn


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a Neo4j database session.

    Yields:
        Neo4j database session
    """
    session = neo4j_conn.get_session()
    try:
        yield session
    finally:
        await session.aclose()
