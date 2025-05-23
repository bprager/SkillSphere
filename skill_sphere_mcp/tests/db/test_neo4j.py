"""Tests for Neo4j database connection management."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from neo4j import AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import AuthError, ServiceUnavailable

from skill_sphere_mcp.db.neo4j import Neo4jConnection, neo4j_conn


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create mock settings."""
    settings = MagicMock()
    settings.neo4j_uri = "bolt://localhost:7687"
    settings.neo4j_user = "neo4j"
    settings.neo4j_password = "password"
    return settings


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Create mock Neo4j driver."""
    return AsyncMock(spec=AsyncGraphDatabase)


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def conn(mock_settings: MagicMock, mock_driver: AsyncMock) -> Neo4jConnection:
    """Create Neo4jConnection instance with mocked dependencies."""
    with (
        patch("skill_sphere_mcp.db.neo4j.get_settings", return_value=mock_settings),
        patch(
            "skill_sphere_mcp.db.neo4j.AsyncGraphDatabase.driver",
            return_value=mock_driver,
        ),
    ):
        return Neo4jConnection()


@pytest.mark.asyncio
async def test_connection_initialization(
    mock_settings: MagicMock, mock_driver: AsyncMock
) -> None:
    """Test Neo4j connection initialization."""
    with (
        patch("skill_sphere_mcp.db.neo4j.get_settings", return_value=mock_settings),
        patch(
            "skill_sphere_mcp.db.neo4j.AsyncGraphDatabase.driver",
            return_value=mock_driver,
        ),
    ):
        conn = Neo4jConnection()

        # Verify driver was created with correct parameters
        mock_driver.assert_called_once_with(
            mock_settings.neo4j_uri,
            auth=(mock_settings.neo4j_user, mock_settings.neo4j_password),
        )


@pytest.mark.asyncio
async def test_verify_connectivity_success(
    conn: Neo4jConnection, mock_driver: AsyncMock
) -> None:
    """Test successful connectivity verification."""
    mock_driver.verify_connectivity.return_value = None

    result = await conn.verify_connectivity()
    assert result is True
    mock_driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_verify_connectivity_service_unavailable(
    conn: Neo4jConnection, mock_driver: AsyncMock
) -> None:
    """Test connectivity verification with service unavailable."""
    mock_driver.verify_connectivity.side_effect = ServiceUnavailable(
        "Connection failed"
    )

    result = await conn.verify_connectivity()
    assert result is False
    mock_driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_verify_connectivity_auth_error(
    conn: Neo4jConnection, mock_driver: AsyncMock
) -> None:
    """Test connectivity verification with authentication error."""
    mock_driver.verify_connectivity.side_effect = AuthError("Invalid credentials")

    result = await conn.verify_connectivity()
    assert result is False
    mock_driver.verify_connectivity.assert_called_once()


@pytest.mark.asyncio
async def test_close(conn: Neo4jConnection, mock_driver: AsyncMock) -> None:
    """Test connection closure."""
    await conn.close()
    mock_driver.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session(
    conn: Neo4jConnection, mock_driver: AsyncMock, mock_session: AsyncMock
) -> None:
    """Test session creation and cleanup."""
    mock_driver.session.return_value = mock_session

    async for session in conn.get_session():
        assert session == mock_session
        # Verify session was created
        mock_driver.session.assert_called_once()

    # Verify session was closed
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_error_handling(
    conn: Neo4jConnection, mock_driver: AsyncMock, mock_session: AsyncMock
) -> None:
    """Test session error handling."""
    mock_driver.session.return_value = mock_session
    mock_session.close.side_effect = RuntimeError("Close error")

    # Session should still be closed even if an error occurs
    async for session in conn.get_session():
        assert session == mock_session
        raise RuntimeError("Test error")

    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_cleanup_on_error(
    conn: Neo4jConnection, mock_driver: AsyncMock, mock_session: AsyncMock
) -> None:
    """Test session cleanup when an error occurs during session usage."""
    mock_driver.session.return_value = mock_session

    with pytest.raises(RuntimeError):
        async for session in conn.get_session():
            assert session == mock_session
            raise RuntimeError("Test error")

    # Verify session was closed even after error
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_global_connection_instance() -> None:
    """Test that the global connection instance is properly initialized."""
    # Verify that neo4j_conn is an instance of Neo4jConnection
    assert isinstance(neo4j_conn, Neo4jConnection)

    # Test that the global instance can be used
    with patch.object(neo4j_conn, "verify_connectivity", return_value=True):
        result = await neo4j_conn.verify_connectivity()
        assert result is True
