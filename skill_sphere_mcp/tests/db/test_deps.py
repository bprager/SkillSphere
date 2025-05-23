"""Tests for database dependencies."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from neo4j import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from skill_sphere_mcp.db.neo4j import neo4j_conn


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    test_app = FastAPI()

    @test_app.get("/test")
    async def test_route(
        db_session: AsyncSession,
    ) -> dict[str, Any]:
        assert db_session is not None
        return {"status": "ok"}

    return test_app


@pytest.mark.asyncio
async def test_get_db_session(test_app: FastAPI) -> None:
    """Test that get_db_session dependency returns a session."""
    # Create a mock session
    mock_session = AsyncMock()

    # Mock the neo4j_conn.get_session method
    with patch.object(neo4j_conn, "get_session") as mock_get_session:
        # Set up the mock to return our mock session
        mock_get_session.return_value = mock_session

        # Create a test client
        client = TestClient(test_app)

        # Make a request to trigger the dependency
        response = client.get("/test")

        # Verify the response
        assert response.status_code == HTTP_200_OK
        assert response.json() == {"status": "ok"}

        # Verify that the session was obtained from neo4j_conn
        mock_get_session.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_session_error_handling(test_app: FastAPI) -> None:
    """Test that get_db_session properly handles errors."""
    # Mock the neo4j_conn.get_session method to raise an error
    with patch.object(neo4j_conn, "get_session") as mock_get_session:
        mock_get_session.side_effect = RuntimeError("Database error")

        # Create a test client
        client = TestClient(test_app)

        # Make a request to trigger the dependency
        response = client.get("/test")

        # Verify that the error is handled appropriately
        assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
