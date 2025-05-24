"""Tests for database dependencies."""

# pylint: disable=redefined-outer-name

from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from neo4j import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from skill_sphere_mcp.db.neo4j import neo4j_conn

get_db_session_dep = Depends(neo4j_conn.get_session)


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI application."""
    test_app = FastAPI()

    @test_app.get("/test", response_model=None)
    async def test_route(
        db_session: AsyncSession = get_db_session_dep,
    ) -> dict[str, Any]:
        # Use the session to trigger any potential errors
        await db_session.run("MATCH (n) RETURN n")
        return {"status": "ok"}

    @test_app.exception_handler(Exception)
    async def generic_exception_handler(exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    return test_app


@pytest.mark.asyncio
async def test_get_db_session(app: FastAPI) -> None:
    """Test that get_db_session dependency returns a session."""
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_session.run.return_value = mock_result

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield mock_session

    app.dependency_overrides[neo4j_conn.get_session] = override_get_session

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_db_session_error_handling(app: FastAPI) -> None:
    """Test that get_db_session properly handles errors."""
    mock_session = AsyncMock()
    mock_session.run.side_effect = RuntimeError("Database error")

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield mock_session

    app.dependency_overrides[neo4j_conn.get_session] = override_get_session

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test")
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
