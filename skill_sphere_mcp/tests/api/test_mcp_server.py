"""Tests for MCP server."""

# pylint: disable=redefined-outer-name

import json
import os
from collections.abc import Generator
from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from skill_sphere_mcp.mcp_server import app, get_neo4j_driver, get_settings
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


def test_get_neo4j_driver() -> None:
    """Test that the Neo4j driver is created correctly."""
    with patch("neo4j.GraphDatabase.driver") as mock_driver:
        get_neo4j_driver()
        mock_driver.assert_called_once()


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


def test_get_entity(client: TestClient) -> None:
    """Test the get entity endpoint."""
    with patch("skill_sphere_mcp.mcp_server.get_neo4j_driver") as mock_get_driver:
        # Create a mock session
        mock_session = MagicMock()
        mock_driver = MagicMock()
        mock_driver.session.return_value.__enter__.return_value = mock_session

        # Set up the mock driver
        mock_get_driver.return_value = mock_driver

        # Create a mock node with the required attributes
        mock_node = MagicMock()
        mock_node.id = 1
        mock_node.labels = {"Node"}
        mock_node.items.return_value = {"name": "TestNode"}.items()

        # Set up the mock session to return our test data
        mock_session.run.return_value.single.return_value = {
            "n": mock_node,
            "rels": [],
        }

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


def test_search_not_implemented(client: TestClient) -> None:
    """Test that search endpoint returns not implemented."""
    response = client.post("/v1/search", json={"query": "test", "k": 10})
    assert response.status_code == HTTP_NOT_IMPLEMENTED
    assert response.json() == {
        "detail": "Free-text semantic search not implemented yet - embed the query first."
    }


def make_aiter(items: list) -> Callable[..., Any]:
    """Return an __aiter__ method for mocking async iteration in tests."""

    def _aiter() -> Any:
        """Async iterator mock for test usage."""
        return AsyncIterator(items)

    return _aiter
