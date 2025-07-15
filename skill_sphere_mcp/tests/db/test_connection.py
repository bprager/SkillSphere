"""Tests for Neo4j connection management."""

# pylint: disable=redefined-outer-name

from builtins import anext
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import pytest_asyncio

from fastapi import HTTPException
from neo4j import AsyncGraphDatabase
from neo4j import AsyncSession
from neo4j.exceptions import AuthError
from neo4j.exceptions import ServiceUnavailable

from skill_sphere_mcp.db.connection import DatabaseConnection


@pytest_asyncio.fixture
def settings() -> MagicMock:
    """Create mock settings."""
    settings = MagicMock()
    settings.neo4j_uri = "bolt://localhost:7687"
    settings.neo4j_user = "neo4j"
    settings.neo4j_password = "neo4j"
    return settings


@pytest_asyncio.fixture
def driver() -> AsyncMock:
    """Create mock Neo4j driver."""
    mock = AsyncMock(spec=AsyncGraphDatabase)
    mock.verify_connectivity = AsyncMock()
    mock.close = AsyncMock()
    mock.session = MagicMock()
    return mock


@pytest_asyncio.fixture
def session_mock() -> AsyncMock:
    """Create mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
def conn(settings: MagicMock, driver: AsyncMock) -> DatabaseConnection:
    """Create DatabaseConnection instance with mocked dependencies."""
    with patch(
        "skill_sphere_mcp.db.connection.GraphDatabase.driver",
        return_value=driver,
    ):
        conn = DatabaseConnection(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
        conn._driver = driver
        return conn


@pytest.mark.asyncio
async def test_connection_initialization(
    settings: MagicMock, driver: AsyncMock
) -> None:
    """Test Neo4j connection initialization."""
    with patch(
        "skill_sphere_mcp.db.connection.GraphDatabase.driver",
        return_value=driver,
    ) as mock_driver:
        conn = DatabaseConnection(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
        await conn.connect()  # Ensure driver is initialized
        # Verify driver was created with correct parameters
        mock_driver.assert_called_once_with(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )


@pytest.mark.asyncio
async def test_verify_connectivity_success(
    conn: DatabaseConnection, driver: AsyncMock
) -> None:
    """Test successful connectivity verification."""
    conn._driver = driver
    driver.verify_connectivity.return_value = None

    result = await conn.verify_connectivity()
    assert result is True
    driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_verify_connectivity_service_unavailable(
    conn: DatabaseConnection, driver: AsyncMock
) -> None:
    """Test connectivity verification with service unavailable."""
    conn._driver = driver
    driver.verify_connectivity.side_effect = ServiceUnavailable("Connection failed")

    result = await conn.verify_connectivity()
    assert result is False


@pytest.mark.asyncio
async def test_verify_connectivity_auth_error(
    conn: DatabaseConnection, driver: AsyncMock
) -> None:
    """Test connectivity verification with authentication error."""
    conn._driver = driver
    driver.verify_connectivity.side_effect = AuthError("Invalid credentials")

    result = await conn.verify_connectivity()
    assert result is False


@pytest.mark.asyncio
async def test_close(conn: DatabaseConnection, driver: AsyncMock) -> None:
    """Test connection closure."""
    conn._driver = driver

    await conn.close()
    driver.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session(
    conn: DatabaseConnection, driver: AsyncMock, session_mock: AsyncMock
) -> None:
    """Test session creation."""
    conn._driver = driver
    driver.session.return_value = session_mock

    session = conn.get_session()
    assert session is session_mock
    # Verify session was created
    driver.session.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_error_handling(
    conn: DatabaseConnection, driver: AsyncMock
) -> None:
    """Test session error handling."""
    conn._driver = driver
    driver.session.side_effect = RuntimeError("Session error")

    session = conn.get_session()
    assert session is None


@pytest.mark.asyncio
async def test_get_session():
    """Test getting a database session."""
    from skill_sphere_mcp.db.deps import get_db_session

    # This should be a generator function, not awaitable
    session_gen = get_db_session()
    session = await anext(session_gen)
    assert session is not None
    # Test that session can be used
    if hasattr(session, 'close') and session.close is not None:
        try:
            await session.close()
        except (TypeError, AttributeError):
            # Session.close() might not be awaitable or might be None
            pass
