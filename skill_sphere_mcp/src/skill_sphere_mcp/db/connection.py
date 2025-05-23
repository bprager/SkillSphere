"""Neo4j database connection management."""

from collections.abc import AsyncGenerator

from neo4j import AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import AuthError, ServiceUnavailable

from skill_sphere_mcp.config.settings import get_settings


class Neo4jConnection:
    """Neo4j connection manager."""

    def __init__(self) -> None:
        settings = get_settings()
        self._driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
        )

    async def verify_connectivity(self) -> bool:
        """Verify database connectivity."""
        try:
            await self._driver.verify_connectivity()
            return True
        except (ServiceUnavailable, AuthError):
            return False

    async def close(self) -> None:
        """Close the database connection."""
        await self._driver.close()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a Neo4j async session."""
        session = self._driver.session()
        try:
            yield session
        finally:
            await session.close()


# Global Neo4j connection instance
neo4j_conn = Neo4jConnection()
