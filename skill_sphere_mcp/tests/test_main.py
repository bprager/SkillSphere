"""Tests for main application module."""

# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from skill_sphere_mcp.main import create_app, lifespan, main

# HTTP status codes
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501
HTTP_OK = 200


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create mock settings."""
    settings = MagicMock()
    settings.host = "0.0.0.0"
    settings.port = 8000
    return settings


@pytest.fixture
def mock_neo4j_conn() -> AsyncMock:
    """Create mock Neo4j connection."""
    conn = AsyncMock()
    conn.verify_connectivity = AsyncMock(return_value=True)
    conn.close = AsyncMock()
    return conn


@pytest.fixture
def mock_tracer() -> MagicMock:
    """Create mock OpenTelemetry tracer."""
    return MagicMock()


def test_create_app() -> None:
    """Test FastAPI application creation."""
    app = create_app()
    assert isinstance(app, FastAPI)
    assert app.title == "Skill Sphere MCP"
    assert app.version == "0.1.0"
    assert app.description == "Management Control Plane for Skill Sphere"


def test_create_app_routes() -> None:
    """Test that all routes are properly included."""
    app = create_app()
    routes = [route.path for route in app.routes if hasattr(route, "path")]
    assert any(route.startswith("/api/v1/") for route in routes)
    assert any(route.startswith("/api/mcp/") for route in routes)


def test_create_app_cors() -> None:
    """Test CORS middleware configuration."""
    app = create_app()
    client = TestClient(app)
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers["access-control-allow-origin"] == "http://example.com"
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_lifespan_success(
    mock_neo4j_conn: AsyncMock, mock_tracer: MagicMock
) -> None:
    """Test successful application lifespan."""
    app = FastAPI()

    with (
        patch("skill_sphere_mcp.main.neo4j_conn", mock_neo4j_conn),
        patch("skill_sphere_mcp.main.setup_telemetry", return_value=mock_tracer),
    ):
        async with lifespan(app) as _:
            assert app.state.tracer == mock_tracer
            mock_neo4j_conn.verify_connectivity.assert_called_once()

        mock_neo4j_conn.close.assert_called_once()


@pytest.mark.asyncio
async def test_lifespan_neo4j_failure(
    mock_neo4j_conn: AsyncMock, mock_tracer: MagicMock
) -> None:
    """Test lifespan with Neo4j connection failure."""
    mock_neo4j_conn.verify_connectivity.return_value = False

    with (
        patch("skill_sphere_mcp.main.neo4j_conn", mock_neo4j_conn),
        patch("skill_sphere_mcp.main.setup_telemetry", return_value=mock_tracer),
        patch("skill_sphere_mcp.main.sys.exit") as mock_exit,
    ):
        async with lifespan(FastAPI()) as _:
            # Should exit before reaching this point due to Neo4j connection failure
            pass
        mock_exit.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_lifespan_telemetry_failure(mock_neo4j_conn: AsyncMock) -> None:
    """Test lifespan with OpenTelemetry setup failure."""
    with (
        patch("skill_sphere_mcp.main.neo4j_conn", mock_neo4j_conn),
        patch("skill_sphere_mcp.main.setup_telemetry", return_value=None),
    ):
        async with lifespan(FastAPI()) as _:
            # No-op since telemetry setup failure is handled gracefully
            pass
        mock_neo4j_conn.verify_connectivity.assert_called_once()


def test_main_function(mock_settings: MagicMock) -> None:
    """Test main function execution."""
    with (
        patch("skill_sphere_mcp.main.get_settings", return_value=mock_settings),
        patch("skill_sphere_mcp.main.uvicorn.run") as mock_run,
    ):
        main()

        mock_run.assert_called_once_with(
            "skill_sphere_mcp.main:create_app",
            host=mock_settings.host,
            port=mock_settings.port,
            factory=True,
            reload=True,
        )


def test_health_check() -> None:
    """Test health check endpoint."""
    app = create_app()
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "healthy"}
