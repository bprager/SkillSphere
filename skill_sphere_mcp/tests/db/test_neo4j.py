"""Test Neo4j database integration."""

# pylint: disable=redefined-outer-name

from builtins import anext
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import pytest_asyncio

from neo4j import AsyncSession
from neo4j.exceptions import AuthError
from neo4j.exceptions import ServiceUnavailable

from skill_sphere_mcp.db.connection import DatabaseConnection


@pytest_asyncio.fixture
def mock_settings() -> MagicMock:
    """Create mock settings."""
    settings = MagicMock()
    settings.neo4j_uri = "bolt://localhost:7687"
    settings.neo4j_user = "neo4j"
    settings.neo4j_password = "password"
    return settings


@pytest_asyncio.fixture
def mock_driver() -> AsyncMock:
    """Create mock Neo4j driver."""
    return AsyncMock()


@pytest_asyncio.fixture
def mock_session() -> AsyncMock:
    """Create mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def mock_transaction():
    # ... existing code ...
    pass


@pytest_asyncio.fixture
async def mock_result():
    # ... existing code ...
    pass


@pytest_asyncio.fixture
def conn(mock_settings: MagicMock, mock_driver: AsyncMock) -> DatabaseConnection:
    """Create DatabaseConnection instance with mocked dependencies."""
    with patch("skill_sphere_mcp.db.connection.GraphDatabase") as mock_graph_db:
        mock_graph_db.driver.return_value = mock_driver
        return DatabaseConnection(
            uri=mock_settings.neo4j_uri,
            user=mock_settings.neo4j_user,
            password=mock_settings.neo4j_password
        )


@pytest.mark.asyncio
async def test_connection_initialization(
    mock_settings: MagicMock, mock_driver: AsyncMock
) -> None:
    """Test connection initialization."""
    with (
        patch("skill_sphere_mcp.db.connection.GraphDatabase") as mock_driver_factory,
    ):
        conn = DatabaseConnection(
            uri=mock_settings.neo4j_uri,
            user=mock_settings.neo4j_user,
            password=mock_settings.neo4j_password
        )
        await conn.connect()
        mock_driver_factory.driver.assert_called_once_with(
            mock_settings.neo4j_uri,
            auth=(mock_settings.neo4j_user, mock_settings.neo4j_password)
        )


@pytest.mark.asyncio
async def test_verify_connectivity_success(
    conn: DatabaseConnection, mock_driver: AsyncMock
) -> None:
    """Test successful connectivity verification."""
    conn._driver = mock_driver
    mock_driver.verify_connectivity.return_value = None

    result = await conn.verify_connectivity()
    assert result is True
    mock_driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_verify_connectivity_service_unavailable(
    conn: DatabaseConnection, mock_driver: AsyncMock
) -> None:
    """Test connectivity verification with service unavailable."""
    conn._driver = mock_driver
    mock_driver.verify_connectivity.side_effect = ServiceUnavailable("Connection failed")

    result = await conn.verify_connectivity()
    assert result is False


@pytest.mark.asyncio
async def test_verify_connectivity_auth_error(
    conn: DatabaseConnection, mock_driver: AsyncMock
) -> None:
    """Test connectivity verification with authentication error."""
    conn._driver = mock_driver
    mock_driver.verify_connectivity.side_effect = AuthError("Invalid credentials")

    result = await conn.verify_connectivity()
    assert result is False


@pytest.mark.asyncio
async def test_close(conn: DatabaseConnection, mock_driver: AsyncMock) -> None:
    """Test connection closure."""
    conn._driver = mock_driver
    await conn.close()
    mock_driver.close.assert_called_once()
    assert conn._driver is None


@pytest.mark.asyncio
async def test_get_session(
    conn: DatabaseConnection, mock_driver: AsyncMock, mock_session: AsyncMock
) -> None:
    """Test session creation and cleanup."""
    conn._driver = mock_driver
    mock_driver.session = MagicMock(return_value=mock_session)

    session = conn.get_session()
    assert session == mock_session
    # Verify session was created
    mock_driver.session.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_error_handling(
    conn: DatabaseConnection, mock_driver: AsyncMock, mock_session: AsyncMock
) -> None:
    """Test session error handling."""
    conn._driver = mock_driver
    mock_driver.session = MagicMock(side_effect=Exception("Session creation failed"))

    session = conn.get_session()
    assert session is None


@pytest.mark.asyncio
async def test_get_session_cleanup_on_error(
    conn: DatabaseConnection, mock_driver: AsyncMock, mock_session: AsyncMock
) -> None:
    """Test session cleanup when an error occurs during session usage."""
    conn._driver = mock_driver
    mock_driver.session = MagicMock(return_value=mock_session)

    session = conn.get_session()
    assert session == mock_session
