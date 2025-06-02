"""Shared pytest fixtures."""

import logging
import os
import sys
import warnings
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from neo4j import AsyncSession

# Suppress SWIG warning
warnings.filterwarnings(
    "ignore", message="builtin type SwigPyPacked has no __module__ attribute"
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Set specific logger levels
logging.getLogger("skill_sphere_mcp").setLevel(logging.DEBUG)
logging.getLogger("skill_sphere_mcp.api.mcp.handlers").setLevel(logging.DEBUG)

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from skill_sphere_mcp.app import create_app
from skill_sphere_mcp.db.connection import neo4j_conn

# Disable OpenTelemetry before any imports
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_TRACES_SAMPLER"] = "always_off"
os.environ["OTEL_EXPORTER_OTLP_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_METRICS_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_LOGS_ENABLED"] = "false"


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    """Create a test client for the FastAPI app."""
    yield TestClient(create_app())


@pytest_asyncio.fixture
async def mock_neo4j_session() -> AsyncGenerator[AsyncMock, None]:
    """Create a mock Neo4j session."""
    session = AsyncMock()
    with patch.object(neo4j_conn, "get_session", return_value=session):
        yield session


@pytest_asyncio.fixture
async def mock_neo4j_session_context() -> AsyncGenerator[AsyncMock, None]:
    """Create a mock Neo4j session context."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_result.single.return_value = None
    mock_result.all.return_value = []
    mock_session.run.return_value = mock_result

    async def mock_get_session() -> AsyncSession:
        return mock_session

    with patch(
        "skill_sphere_mcp.db.connection.neo4j_conn.get_session",
        mock_get_session,
    ):
        yield mock_session


@pytest.fixture(autouse=True)
def mock_embedding_model():
    with patch("skill_sphere_mcp.api.mcp.handlers.MODEL") as mock_model:
        # Create a deterministic embedding for test cases
        test_embedding = np.zeros(384)  # All zeros vector for test cases
        query_embedding = np.ones(384)  # All ones vector for query

        def get_embedding(text: str) -> np.ndarray:
            # Return test_embedding for test-related text, query_embedding for query
            if text.lower() == "test":
                return query_embedding
            return test_embedding

        mock_model.get_embedding.side_effect = get_embedding
        yield mock_model
