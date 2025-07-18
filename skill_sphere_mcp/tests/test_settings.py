"""Test settings configuration."""

import os
from collections.abc import Generator

import pytest

from skill_sphere_mcp.config.settings import Settings


@pytest.fixture(autouse=True)
def test_env() -> Generator[None, None, None]:
    """Set up test environment variables."""
    # Store original environment
    original_env = dict(os.environ)
    
    # Set test environment variables with correct prefix
    os.environ.update({
        "SKILL_SPHERE_MCP_HOST": "0.0.0.0",
        "SKILL_SPHERE_MCP_PORT": "8000",
        "SKILL_SPHERE_MCP_NEO4J_URI": "bolt://localhost:7687",
        "SKILL_SPHERE_MCP_NEO4J_USER": "neo4j",
        "SKILL_SPHERE_MCP_NEO4J_PASSWORD": "test_password",
        "SKILL_SPHERE_OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
        "SKILL_SPHERE_OTEL_SERVICE_NAME": "mcp-server-test",
        "SKILL_SPHERE_MCP_CLIENT_NAME": "SkillSphere-Test",
        "SKILL_SPHERE_MCP_CLIENT_VERSION": "1.0.0",
        "SKILL_SPHERE_MCP_CLIENT_ENVIRONMENT": "test",
        "SKILL_SPHERE_MCP_CLIENT_FEATURES": "cv,search,matching",
        "SKILL_SPHERE_MCP_INSTRUCTIONS": "Test instructions",
    })
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def test_settings() -> Settings:
    """Get test settings instance."""
    return Settings() 