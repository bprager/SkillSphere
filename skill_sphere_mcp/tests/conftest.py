"""Test configuration and fixtures."""

import logging
import os
import sys
import warnings

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import numpy as np
import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from neo4j import AsyncSession

from skill_sphere_mcp.app import create_app
from skill_sphere_mcp.models.embedding import get_embedding_model


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress SWIG deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="_swig")

# Disable OpenTelemetry before any imports
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_METRICS_ENABLED"] = "false"
os.environ["OTEL_EXPORTER_OTLP_LOGS_ENABLED"] = "false"

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


@pytest_asyncio.fixture
async def mock_neo4j_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def mock_embedding_model() -> AsyncMock:
    """Create a mock embedding model."""
    return AsyncMock(spec=get_embedding_model())


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    """Create a test client."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_numpy_random() -> None:
    """Mock numpy random functions for deterministic testing."""
    np.random.seed(42)
