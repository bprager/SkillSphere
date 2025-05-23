"""Tests for settings module."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from skill_sphere_mcp.config.settings import Settings, get_settings


def test_settings_defaults() -> None:
    """Test settings with default values."""
    settings = Settings()
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.neo4j_user == "neo4j"


def test_settings_from_env() -> None:
    """Test settings loaded from environment variables."""
    env_vars = {
        "MCP_HOST": "localhost",
        "MCP_PORT": "9000",
        "MCP_NEO4J_URI": "bolt://localhost:7687",
        "MCP_NEO4J_USER": "test_user",
        "MCP_NEO4J_PASSWORD": "test_pass",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
        "OTEL_SERVICE_NAME": "test-service",
    }

    with patch.dict(os.environ, env_vars):
        settings = Settings()
        assert settings.host == "localhost"
        assert settings.port == 9000
        assert settings.neo4j_uri == "bolt://localhost:7687"
        assert settings.neo4j_user == "test_user"
        assert settings.neo4j_password == "test_pass"
        assert settings.otel_endpoint == "http://localhost:4317"
        assert settings.otel_service_name == "test-service"


def test_settings_validation() -> None:
    """Test settings validation."""
    # Missing required fields
    with pytest.raises(ValidationError):
        Settings(neo4j_uri="", neo4j_password="")

    # Invalid port number
    with pytest.raises(ValidationError):
        Settings(port=-1)

    # Invalid port number (too high)
    with pytest.raises(ValidationError):
        Settings(port=70000)


def test_get_settings_caching() -> None:
    """Test settings caching."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2  # Should return cached instance


def test_settings_extra_fields() -> None:
    """Test that extra fields are ignored."""
    settings = Settings(unknown_field="value")  # type: ignore
    assert not hasattr(settings, "unknown_field")
