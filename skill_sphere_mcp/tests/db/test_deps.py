"""Tests for database dependencies."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from typing import Dict, Any
from neo4j import AsyncSession

from skill_sphere_mcp.db.deps import get_db_session
from skill_sphere_mcp.db.neo4j import neo4j_conn


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()

    @app.get("/test")
    async def test_route(
        session: AsyncSession = Depends(get_db_session),
    ) -> Dict[str, Any]:
        return {"status": "ok"}

    return app


@pytest.mark.asyncio
async def test_get_db_session(app: FastAPI) -> None:
    """Test that get_db_session dependency returns a session."""
    # Create a mock session
    mock_session = AsyncMock()

    # Mock the neo4j_conn.get_session method
    with patch.object(neo4j_conn, "get_session") as mock_get_session:
        # Set up the mock to return our mock session
        mock_get_session.return_value = mock_session

        # Create a test client
        client = TestClient(app)

        # Make a request to trigger the dependency
        response = client.get("/test")

        # Verify the response
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

        # Verify that the session was obtained from neo4j_conn
        mock_get_session.assert_called_once()


@pytest.mark.asyncio
async def test_get_db_session_error_handling(app: FastAPI) -> None:
    """Test that get_db_session properly handles errors."""
    # Mock the neo4j_conn.get_session method to raise an error
    with patch.object(neo4j_conn, "get_session") as mock_get_session:
        mock_get_session.side_effect = RuntimeError("Database error")

        # Create a test client
        client = TestClient(app)

        # Make a request to trigger the dependency
        response = client.get("/test")

        # Verify that the error is handled appropriately
        assert response.status_code == 500
