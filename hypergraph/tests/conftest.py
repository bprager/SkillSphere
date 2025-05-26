"""Pytest configuration and fixtures."""

# pylint: disable=import-error, redefined-outer-name
import os
from pathlib import Path
from typing import Generator

import pytest
from neo4j import GraphDatabase

from hypergraph.core.config import Settings


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_pass="test",
        ollama_base_url="http://localhost:11434",
        graph_schema_yaml="tests/data/schema.yaml",
        doc_root="tests/data/docs",
        registry_path="tests/data/registry.db",
        faiss_index_path="tests/data/faiss.index",
    )


@pytest.fixture
def neo4j_driver(settings: Settings) -> Generator:
    """Create a Neo4j test driver."""
    driver = GraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_pass)
    )
    yield driver
    driver.close()


@pytest.fixture(autouse=True)
def setup_test_env(settings: Settings) -> Generator:
    """Set up test environment variables."""
    # Store original env vars
    original_env = dict(os.environ)

    # Set test env vars
    os.environ.update(
        {
            "NEO4J_URI": settings.neo4j_uri,
            "NEO4J_USER": settings.neo4j_user,
            "NEO4J_PASS": settings.neo4j_pass,
            "OLLAMA_BASE_URL": settings.ollama_base_url,
        }
    )

    # Create test directories
    Path(settings.doc_root).mkdir(parents=True, exist_ok=True)
    Path(settings.registry_path).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.faiss_index_path).parent.mkdir(parents=True, exist_ok=True)

    yield

    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env)
