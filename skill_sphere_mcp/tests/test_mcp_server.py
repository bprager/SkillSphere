"""Tests for MCP server."""

# pylint: disable=redefined-outer-name

import json
import os
from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from skill_sphere_mcp.db.connection import Neo4jConnection
from skill_sphere_mcp.mcp_server import app, get_settings
from tests.graph.test_node2vec import AsyncIterator

# Disable OpenTelemetry before any imports
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_SAMPLER"] = "always_off"
os.environ["OTEL_EXPORTER_OTLP_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_METRICS_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_LOGS_ENABLED"] = "false"

DEFAULT_PORT = 8000
HTTP_OK = 200
HTTP_NOT_IMPLEMENTED = 501
TEST_RESULTS_COUNT = 2


@pytest.fixture(autouse=True)
def disable_tracing() -> Generator[None, None, None]:
    """Disable OpenTelemetry tracing during tests."""
    # Save original environment
    original_env = dict(os.environ)

    # Disable OpenTelemetry
    os.environ["OTEL_SDK_DISABLED"] = "true"
    os.environ["OTEL_TRACES_SAMPLER"] = "always_off"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_get_settings() -> None:
    """Test that the settings are loaded correctly."""
    settings = get_settings()
    assert settings.host == "0.0.0.0"
    assert settings.port == DEFAULT_PORT


@pytest.mark.asyncio
async def test_get_neo4j_driver() -> None:
    """Test that the Neo4j driver is created correctly."""
    mock_driver = AsyncMock()
    mock_driver.verify_connectivity = AsyncMock(return_value=True)
    with patch("neo4j.AsyncGraphDatabase.driver", return_value=mock_driver):
        conn = Neo4jConnection()
        assert await conn.verify_connectivity() is True


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/v1/healthz")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_get_entity(client: TestClient) -> None:
    """Test the get entity endpoint."""
    with patch(
        "skill_sphere_mcp.db.connection.neo4j_conn.get_session"
    ) as mock_get_session:
        # Create a mock session
        mock_session = AsyncMock()
        mock_get_session.return_value = AsyncIterator([mock_session])

        # Create a mock node with the required attributes
        mock_node = MagicMock()
        mock_node.id = 1
        mock_node.labels = {"Node"}
        mock_node.items.return_value = {"name": "TestNode"}.items()

        # Set up the mock session to return our test data
        mock_result = AsyncMock()
        mock_result.single.return_value = {
            "n": mock_node,
            "rels": [],
        }
        mock_session.run.return_value = mock_result

        # Make the request
        response = client.get("/v1/entity/1")
        assert response.status_code == HTTP_OK

        # Verify the mock session was called with the correct query and parameters
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "MATCH (n) WHERE id(n) = $id" in call_args[0][0]  # Check query
        assert call_args[1]["id"] == 1  # Check parameters

        # Verify the data directly from the mock session
        result = mock_session.run.return_value.single.return_value
        print(
            json.dumps(
                {
                    "node": {
                        "id": result["n"].id,
                        "labels": list(result["n"].labels),
                        "properties": dict(result["n"]),
                    },
                    "relationships": result["rels"],
                },
                indent=2,
            )
        )


@patch("skill_sphere_mcp.routes.MODEL")
def test_search_success(mock_model: MagicMock, client: TestClient) -> None:
    """Test that search endpoint returns results correctly."""
    # Mock the model's encode method
    mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])  # Mock embedding vector

    # Mock Neo4j session and results
    with patch(
        "skill_sphere_mcp.db.connection.neo4j_conn.get_session"
    ) as mock_get_session:
        mock_session = AsyncMock()
        mock_get_session.return_value = AsyncIterator([mock_session])

        # Set up mock results as a real async generator
        async def async_gen():
            yield {"id": 1, "embedding": np.array([0.1, 0.2, 0.3])}
            yield {"id": 2, "embedding": np.array([0.2, 0.3, 0.4])}

        mock_session.run.return_value = async_gen()

        # Make the request
        response = client.post("/v1/search", json={"query": "test", "k": 2})
        assert response.status_code == HTTP_OK

        # Verify response format and content
        results = response.json()
        assert len(results) == TEST_RESULTS_COUNT
        assert all(isinstance(r["entity_id"], str) for r in results)
        assert all(isinstance(r["score"], float) for r in results)
        assert all(0 <= r["score"] <= 1 for r in results)

        # Verify the model was called with the query
        mock_model.encode.assert_called_once_with("test")

        # Verify Neo4j query was executed
        mock_session.run.assert_called_once()
        call_args = mock_session.run.call_args
        assert "MATCH (n)" in call_args[0][0]  # Check query contains MATCH
        assert "embedding" in call_args[0][0]  # Check query references embedding


def make_aiter(items: list) -> Callable[..., Any]:
    """Return an __aiter__ method for mocking async iteration in tests."""

    def _aiter() -> Any:
        """Async iterator mock for test usage."""
        return AsyncIterator(items)

    return _aiter
