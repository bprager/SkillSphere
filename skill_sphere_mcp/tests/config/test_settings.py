"""Tests for settings module."""

# pylint: disable=redefined-outer-name

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from skill_sphere_mcp.config.settings import Settings, get_settings

DEFAULT_PORT = 8000
TEST_PORT = 9000


def test_settings_defaults() -> None:
    """Test settings with default values."""
    settings = Settings(neo4j_uri="bolt://localhost:7687", neo4j_password="test_pass")
    assert settings.host == "0.0.0.0"
    assert settings.port == DEFAULT_PORT
    assert settings.neo4j_user == "neo4j"


def test_settings_from_env() -> None:
    """Test settings loaded from environment variables."""
    env_vars = {
        "SKILL_SPHERE_MCP_HOST": "localhost",
        "SKILL_SPHERE_MCP_PORT": str(TEST_PORT),
        "SKILL_SPHERE_MCP_NEO4J_URI": "bolt://localhost:7687",
        "SKILL_SPHERE_MCP_NEO4J_USER": "test_user",
        "SKILL_SPHERE_MCP_NEO4J_PASSWORD": "test_pass",
        "SKILL_SPHERE_MCP_OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
        "SKILL_SPHERE_MCP_OTEL_SERVICE_NAME": "test-service",
    }
    with patch.dict(os.environ, env_vars):
        settings = Settings(
            neo4j_uri="bolt://localhost:7687", neo4j_password="test_pass"
        )
        assert settings.host == "localhost"
        assert settings.port == TEST_PORT
        assert settings.neo4j_uri == "bolt://localhost:7687"
        assert settings.neo4j_user == "test_user"
        assert settings.neo4j_password == "test_pass"
        assert settings.otel_exporter_otlp_endpoint == "http://localhost:4317"
        assert settings.otel_service_name == "test-service"


def test_settings_invalid_port() -> None:
    """Test settings with invalid port numbers."""
    env = {
        "SKILL_SPHERE_MCP_NEO4J_URI": "bolt://localhost:7687",
        "SKILL_SPHERE_MCP_NEO4J_PASSWORD": "test_pass"
    }
    with patch.dict(os.environ, {**env, "SKILL_SPHERE_MCP_PORT": "-1"}, clear=True):
        with pytest.raises(ValidationError):
            Settings(neo4j_uri="bolt://localhost:7687", neo4j_password="test_pass")
    with patch.dict(os.environ, {**env, "SKILL_SPHERE_MCP_PORT": "70000"}, clear=True):
        with pytest.raises(ValidationError):
            Settings(neo4j_uri="bolt://localhost:7687", neo4j_password="test_pass")


def test_get_settings_caching() -> None:
    """Test settings caching."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Should return cached instance


def test_settings_extra_fields() -> None:
    """Test that extra fields are ignored."""
    settings = Settings(neo4j_uri="bolt://localhost:7687", neo4j_password="test_pass")
    assert not hasattr(settings, "unknown_field")


def test_teardown():
    os.environ.pop("PYTEST_CURRENT_TEST", None)
