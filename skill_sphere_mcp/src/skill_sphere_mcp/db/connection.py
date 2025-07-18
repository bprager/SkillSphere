"""Database connection management."""

import logging
from typing import cast

from neo4j import AsyncDriver, AsyncSession, GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, uri: str, user: str, password: str) -> None:
        """Initialize database connection."""
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: AsyncDriver | None = None

    async def connect(self) -> None:
        """Establish database connection."""
        try:
            driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver = cast(AsyncDriver, driver)
            logger.info("Database connection established")
        except (ValueError, TypeError, AuthError, ServiceUnavailable) as e:
            logger.error("Failed to establish database connection: %s", e)
            raise
        # pylint: disable-next=W0718
        except Exception as e:
            # Broad catch for unexpected errors in establishing connection (should not crash app)
            logger.error("Unexpected error establishing database connection: %s", e)
            raise

    async def verify_connectivity(self) -> bool:
        """Verify database connectivity."""
        if not self._driver:
            return False

        try:
            await self._driver.verify_connectivity()
        except ServiceUnavailable:
            logger.error("Database service unavailable")
            return False
        except AuthError:
            logger.error("Database authentication failed")
            return False
        except (RuntimeError, ValueError) as e:
            logger.error("Database connectivity check failed: %s", e)
            return False
        # pylint: disable-next=W0718
        except Exception as e:
            # Broad catch for unexpected errors during connectivity check (should not crash app)
            logger.error("Unexpected error during connectivity check: %s", e)
            return False
        return True

    async def close(self) -> None:
        """Close database connection."""
        if self._driver is not None:
            try:
                await self._driver.close()
            except (RuntimeError, ValueError) as e:
                logger.error("Error closing database connection: %s", e)
            # pylint: disable-next=W0718
            except Exception as e:
                # Broad catch for unexpected errors during connection close (should not crash app)
                logger.error("Unexpected error closing database connection: %s", e)
            finally:
                self._driver = None
                logger.info("Database connection closed")

    def get_session(self) -> AsyncSession | None:
        """Get database session."""
        if not self._driver:
            logger.error("No database driver available")
            return None

        try:
            return self._driver.session()
        except (RuntimeError, ValueError, AttributeError) as e:
            logger.error("Failed to create database session: %s", e)
            return None
        # pylint: disable-next=W0718
        except Exception as e:
            # Broad catch for unexpected errors during session creation (should not crash app)
            logger.error("Unexpected error creating database session: %s", e)
            return None
