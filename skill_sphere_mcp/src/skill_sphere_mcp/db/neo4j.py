"""Neo4j database connection and session management."""

import logging
from typing import AsyncGenerator

from neo4j import AsyncDriver, AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Manages Neo4j database connection and session lifecycle."""

    def __init__(self) -> None:
        """Initialize Neo4j connection with settings."""
        settings = get_settings()
        self._driver: AsyncDriver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        await self._driver.close()

    async def verify_connectivity(self) -> bool:
        """Verify Neo4j database connectivity."""
        try:
            await self._driver.verify_connectivity()
            return True
        except ServiceUnavailable as exc:
            logger.error("Failed to connect to Neo4j: %s", exc)
            return False

    async def get_session(self) -> AsyncGenerator:
        """Get an async Neo4j session."""
        async with self._driver.session() as session:
            yield session


# Global connection instance
neo4j_conn = Neo4jConnection()
