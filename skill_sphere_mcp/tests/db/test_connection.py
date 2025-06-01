"""Tests for Neo4j connection management."""

# pylint: disable=redefined-outer-name

from builtins import anext
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from neo4j import AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import AuthError, ServiceUnavailable

from skill_sphere_mcp.db.connection import Neo4jConnection


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
def conn(settings: MagicMock, driver: AsyncMock) -> Neo4jConnection:
    """Create Neo4jConnection instance with mocked dependencies."""
    with (
        patch("skill_sphere_mcp.db.connection.get_settings", return_value=settings),
        patch(
            "skill_sphere_mcp.db.connection.AsyncGraphDatabase.driver",
            return_value=driver,
        ),
    ):
        return Neo4jConnection()


@pytest.mark.asyncio
async def test_connection_initialization(
    settings: MagicMock, driver: AsyncMock
) -> None:
    """Test Neo4j connection initialization."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None

    with (
        patch(
            "skill_sphere_mcp.db.connection.get_settings",
            return_value=settings,
        ),
        patch(
            "skill_sphere_mcp.db.connection.AsyncGraphDatabase.driver",
            return_value=driver,
        ) as mock_driver,
    ):
        conn = (
            Neo4jConnection()
        )  # Create the connection to trigger driver initialization
        await conn.connect()  # Ensure driver is initialized
        # Verify driver was created with correct parameters
        mock_driver.assert_called_once_with(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )


@pytest.mark.asyncio
async def test_verify_connectivity_success(
    conn: Neo4jConnection, driver: AsyncMock
) -> None:
    """Test successful connectivity verification."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver
    driver.verify_connectivity.return_value = None

    result = await conn.verify_connectivity()
    assert result is True
    driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_verify_connectivity_service_unavailable(
    conn: Neo4jConnection, driver: AsyncMock
) -> None:
    """Test connectivity verification with service unavailable."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver
    driver.verify_connectivity.side_effect = ServiceUnavailable("Connection failed")

    result = await conn.verify_connectivity()
    assert result is False
    driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_verify_connectivity_auth_error(
    conn: Neo4jConnection, driver: AsyncMock
) -> None:
    """Test connectivity verification with authentication error."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver
    driver.verify_connectivity.side_effect = AuthError("Invalid credentials")

    result = await conn.verify_connectivity()
    assert result is False
    driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_close(conn: Neo4jConnection, driver: AsyncMock) -> None:
    """Test connection closure."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver

    await conn.close()
    driver.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session(
    conn: Neo4jConnection, driver: AsyncMock, session_mock: AsyncMock
) -> None:
    """Test session creation and cleanup."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver
    driver.session.return_value = session_mock

    async for session in conn.get_session():
        assert session is session_mock
        # Verify session was created
        driver.session.assert_called_once()

    # Verify session was closed
    session_mock.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_error_handling(
    conn: Neo4jConnection, driver: AsyncMock, session_mock: AsyncMock
) -> None:
    """Test session error handling."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver
    driver.session.return_value = session_mock
    session_mock.close.side_effect = RuntimeError("Close error")

    agen = conn.get_session()
    with pytest.raises(RuntimeError, match="Close error"):
        session = await anext(agen)
        assert session is session_mock
        await agen.athrow(RuntimeError("Test error"))
    session_mock.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_cleanup_on_error(
    conn: Neo4jConnection, driver: AsyncMock, session_mock: AsyncMock
) -> None:
    """Test session cleanup when an error occurs during session usage."""
    # Reset singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    conn._driver = driver
    driver.session.return_value = session_mock

    agen = conn.get_session()
    with pytest.raises(RuntimeError, match="Test error"):
        session = await anext(agen)
        assert session is session_mock
        await agen.athrow(RuntimeError("Test error"))
    session_mock.close.assert_called_once()
