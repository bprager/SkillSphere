"""Neo4j database connection management."""

import logging

from typing import AsyncGenerator
from typing import Optional

from fastapi import HTTPException
from neo4j import AsyncDriver
from neo4j import AsyncGraphDatabase
from neo4j import AsyncSession
from neo4j.exceptions import AuthError
from neo4j.exceptions import ServiceUnavailable

from skill_sphere_mcp.config.settings import get_settings


logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Neo4j connection manager."""

    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[AsyncDriver] = None

    def __new__(cls) -> "Neo4jConnection":
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Neo4j connection."""
        if self._driver is None:
            self._initialize_driver()

    def _initialize_driver(self) -> None:
        """Initialize Neo4j driver."""
        settings = get_settings()
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            logger.info("Neo4j driver initialized successfully")
        except ServiceUnavailable as e:
            logger.error("Failed to connect to Neo4j: %s", e)
            raise

    @property
    def driver(self) -> AsyncDriver:
        """Get Neo4j driver instance."""
        if self._driver is None:
            self._initialize_driver()
        return self._driver

    async def connect(self) -> None:
        """Connect to Neo4j database."""
        if self._driver is None:
            self._initialize_driver()
        await self.verify_connectivity()

    async def verify_connectivity(self) -> bool:
        """Verify database connectivity."""
        if self._driver is None:
            self._initialize_driver()
        try:
            await self._driver.verify_connectivity()
            return True
        except ServiceUnavailable as e:
            logger.error("Service unavailable: %s", e)
            raise HTTPException(status_code=503, detail="Database service unavailable") from e
        except AuthError as e:
            logger.error("Authentication failed: %s", e)
            raise HTTPException(status_code=401, detail="Database authentication failed") from e
        except Exception as e:
            logger.error("Connection verification failed: %s", e)
            raise HTTPException(status_code=500, detail="Database connection failed") from e

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a Neo4j database session.

        Yields:
            Neo4j database session
        """
        if self._driver is None:
            self._initialize_driver()
        session = self._driver.session()
        try:
            yield session
        finally:
            await session.close()

    async def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")


# Create a singleton instance
neo4j_conn = Neo4jConnection()
