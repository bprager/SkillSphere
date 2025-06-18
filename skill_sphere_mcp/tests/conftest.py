"""Test configuration and fixtures."""

import logging
import os

from typing import AsyncGenerator
from typing import Generator
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from neo4j import AsyncSession
from neo4j import Driver
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from skill_sphere_mcp.app import create_app
from skill_sphere_mcp.config.settings import get_test_settings
from skill_sphere_mcp.config.settings import settings


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment."""
    # Store original value if it exists
    original_value = os.environ.get("PYTEST_CURRENT_TEST")
    # Set test flag
    os.environ["PYTEST_CURRENT_TEST"] = "1"
    yield
    # Restore original value or remove if it didn't exist
    if original_value is not None:
        os.environ["PYTEST_CURRENT_TEST"] = original_value
    else:
        os.environ.pop("PYTEST_CURRENT_TEST", None)


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Create a test FastAPI application."""
    with patch("skill_sphere_mcp.config.settings.get_settings", return_value=get_test_settings()):
        return create_app()


@pytest.fixture(scope="session")
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def mock_neo4j_driver() -> Generator[Driver, None, None]:
    """Create a mock Neo4j driver."""
    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        yield driver
    except ServiceUnavailable as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        raise
    finally:
        driver.close()


@pytest.fixture(scope="session")
async def mock_neo4j_session(
    mock_neo4j_driver: Driver,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a mock Neo4j session."""
    async with mock_neo4j_driver.session() as session:
        yield session


@pytest.fixture(scope="session")
def auth_manager():
    """Create an auth manager instance."""
    from skill_sphere_mcp.auth.pat import pat_auth
    return pat_auth


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.run = AsyncMock()

    def run_side_effect(*args, **kwargs):
        query = args[0] if args else ""
        params = args[1] if len(args) > 1 else kwargs

        # For get_entity_by_id (MATCH (n) WHERE n.id = $id)
        if "MATCH (n) WHERE n.id = $id" in query:
            # Simulate not found for 'nonexistent'
            if params and (params.get("id") == "nonexistent"):
                mock_result = AsyncMock()
                mock_result.single = AsyncMock(return_value=None)
                return mock_result
            # Otherwise, return a dummy entity with relationships
            mock_result = AsyncMock()
            mock_result.single = AsyncMock(
                return_value={
                    "n": {"id": "someid", "name": "Some Entity"},
                    "labels": ["Entity"],
                    "relationships": [
                        {
                            "type": "RELATES_TO",
                            "target": {"id": "otherid", "name": "Other Entity"},
                            "target_labels": ["Entity"],
                        }
                    ],
                }
            )
            return mock_result

        # For match_role (MATCH (p:Person))
        elif "MATCH (p:Person)" in query:
            mock_result = AsyncMock()
            mock_result.all = AsyncMock(
                return_value=[
                    {
                        "p": {
                            "id": "1",
                            "name": "Test Person",
                            "skills": ["Python", "FastAPI"],
                            "experience": {"Python": 5, "FastAPI": 3},
                        }
                    }
                ]
            )
            return mock_result

        # For explain_match (MATCH (s:Skill))
        elif "MATCH (s:Skill" in query:
            mock_result = AsyncMock()
            mock_result.single = AsyncMock(
                return_value={
                    "s": {"id": "1", "name": "Python"},
                    "projects": [
                        {
                            "id": "p1",
                            "name": "Project A",
                            "description": "Python project",
                        }
                    ],
                    "certifications": [
                        {
                            "id": "c1",
                            "name": "Python Cert",
                            "description": "Python certification",
                        }
                    ],
                }
            )
            return mock_result

        # For graph_search (MATCH (n))
        elif "MATCH (n)" in query:
            mock_result = AsyncMock()
            mock_result.all = AsyncMock(
                return_value=[
                    {
                        "n": {
                            "id": "1",
                            "name": "Python",
                            "type": "Skill",
                            "description": "Python programming language",
                            "labels": ["Skill"],
                            "properties": {
                                "name": "Python",
                                "description": "Python programming language",
                            },
                        }
                    },
                    {
                        "n": {
                            "id": "2",
                            "name": "FastAPI",
                            "type": "Skill",
                            "description": "FastAPI web framework",
                            "labels": ["Skill"],
                            "properties": {
                                "name": "FastAPI",
                                "description": "FastAPI web framework",
                            },
                        }
                    },
                ]
            )
            return mock_result

        # Default case
        mock_result = AsyncMock()
        mock_result.all = AsyncMock(return_value=[])
        return mock_result

    session.run.side_effect = run_side_effect
    return session
