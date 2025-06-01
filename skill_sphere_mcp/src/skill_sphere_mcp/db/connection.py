"""Neo4j connection management."""

from typing import AsyncGenerator, Optional

from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from ..config.settings import get_settings


class Neo4jConnection:
    """Neo4j connection manager."""

    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[AsyncDriver] = None

    def __new__(cls) -> "Neo4jConnection":
        """Create a singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the connection manager."""
        if self._driver is None:
            settings = get_settings()
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )

    async def connect(self) -> None:
        """Connect to the database."""
        if self._driver is None:
            settings = get_settings()
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            await self._driver.verify_connectivity()

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def verify_connectivity(self) -> bool:
        """Verify database connectivity.

        Returns:
            True if connection is successful, False otherwise
        """
        if self._driver is None:
            return False
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception:
            return False

    async def close(self) -> None:
        """Close the database connection."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session.

        Yields:
            Neo4j database session
        """
        if self._driver is None:
            raise RuntimeError("Database not connected")
        session = self._driver.session()
        try:
            yield session
        finally:
            await session.close()


neo4j_conn = Neo4jConnection()
