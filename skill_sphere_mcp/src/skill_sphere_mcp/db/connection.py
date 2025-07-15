"""Database connection management."""

import logging

from typing import Optional
from typing import cast

from neo4j import AsyncDriver
from neo4j import AsyncSession
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError
from neo4j.exceptions import ServiceUnavailable


logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        """Initialize database connection."""
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[AsyncDriver] = None

    async def connect(self) -> None:
        """Establish database connection."""
        try:
            driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            self._driver = cast(AsyncDriver, driver)
            logger.info("Database connection established")
        except Exception as e:
            logger.error("Failed to establish database connection: %s", e)
            raise

    async def verify_connectivity(self) -> bool:
        """Verify database connectivity."""
        if not self._driver:
            return False

        try:
            await self._driver.verify_connectivity()
            return True
        except ServiceUnavailable:
            logger.error("Database service unavailable")
            return False
        except AuthError:
            logger.error("Database authentication failed")
            return False
        except Exception as e:
            logger.error("Database connectivity check failed: %s", e)
            return False

    async def close(self) -> None:
        """Close database connection."""
        if self._driver is not None:
            try:
                await self._driver.close()
            except Exception as e:
                logger.error("Error closing database connection: %s", e)
            finally:
                self._driver = None
                logger.info("Database connection closed")

    def get_session(self) -> Optional[AsyncSession]:
        """Get database session."""
        if not self._driver:
            logger.error("No database driver available")
            return None

        try:
            return self._driver.session()
        except Exception as e:
            logger.error("Failed to create database session: %s", e)
            return None
