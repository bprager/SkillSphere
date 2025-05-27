"""Tests for application settings."""

import os

import pytest
from pydantic import ValidationError

from skill_sphere_mcp.config.settings import ClientInfo, Settings


def test_client_info_defaults() -> None:
    """Test ClientInfo default values."""
    client_info = ClientInfo()
    assert client_info.name == "SkillSphere"
    assert client_info.version == "1.0.0"
    assert client_info.environment == "development"
    assert "cv" in client_info.features
    assert "search" in client_info.features
    assert "matching" in client_info.features


def test_client_info_custom_values() -> None:
    """Test ClientInfo with custom values."""
    client_info = ClientInfo(
        name="CustomApp",
        version="2.0.0",
        environment="production",
        features=["cv", "search"],
    )
    assert client_info.name == "CustomApp"
    assert client_info.version == "2.0.0"
    assert client_info.environment == "production"
    assert client_info.features == ["cv", "search"]


def test_client_info_validation() -> None:
    """Test ClientInfo validation."""
    with pytest.raises(ValidationError):
        ClientInfo(name="")  # Empty name should fail

    with pytest.raises(ValidationError):
        ClientInfo(version="invalid")  # Invalid version format

    with pytest.raises(ValidationError):
        ClientInfo(environment="invalid")  # Invalid environment


def test_client_info_from_env() -> None:
    """Test ClientInfo loading from environment variables."""
    env_vars = {
        "MCP_CLIENT_NAME": "EnvApp",
        "MCP_CLIENT_VERSION": "3.0.0",
        "MCP_CLIENT_ENVIRONMENT": "staging",
        "MCP_CLIENT_FEATURES": "cv,search,matching",
    }

    # Save original env vars
    original_env = {k: os.environ.get(k) for k in env_vars}

    try:
        # Set test env vars
        for k, v in env_vars.items():
            os.environ[k] = v

        client_info = ClientInfo()
        assert client_info.name == "EnvApp"
        assert client_info.version == "3.0.0"
        assert client_info.environment == "staging"
        assert client_info.features == ["cv", "search", "matching"]
    finally:
        # Restore original env vars
        for k, v in original_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_settings_client_info_integration() -> None:
    """Test Settings integration with ClientInfo."""
    settings = Settings()
    assert isinstance(settings.client_info, ClientInfo)
    assert settings.client_info.name == "SkillSphere"
    assert "cv" in settings.client_info.features


def test_settings_client_info_env_override() -> None:
    """Test Settings client info environment override."""
    env_vars = {
        "MCP_CLIENT_NAME": "EnvApp",
        "MCP_CLIENT_VERSION": "3.0.0",
        "MCP_CLIENT_ENVIRONMENT": "staging",
        "MCP_CLIENT_FEATURES": "cv,search,matching",
    }

    # Save original env vars
    original_env = {k: os.environ.get(k) for k in env_vars}

    try:
        # Set test env vars
        for k, v in env_vars.items():
            os.environ[k] = v

        settings = Settings()
        assert settings.client_info.name == "EnvApp"
        assert settings.client_info.version == "3.0.0"
        assert settings.client_info.environment == "staging"
        assert settings.client_info.features == ["cv", "search", "matching"]
    finally:
        # Restore original env vars
        for k, v in original_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_client_info_feature_validation() -> None:
    """Test ClientInfo feature validation."""
    # Test empty features list
    with pytest.raises(ValidationError):
        ClientInfo(features=[])

    # Test duplicate features
    with pytest.raises(ValidationError):
        ClientInfo(features=["cv", "cv"])

    # Test invalid feature name
    with pytest.raises(ValidationError):
        ClientInfo(features=["invalid_feature"])


def test_client_info_serialization() -> None:
    """Test ClientInfo serialization."""
    client_info = ClientInfo(
        name="TestApp",
        version="1.0.0",
        environment="test",
        features=["cv", "search"],
    )

    # Test dict conversion
    data = client_info.model_dump()
    assert data["name"] == "TestApp"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "test"
    assert data["features"] == ["cv", "search"]

    # Test JSON conversion
    json_data = client_info.model_dump_json()
    assert '"name": "TestApp"' in json_data
    assert '"features": ["cv", "search"]' in json_data


def test_client_info_immutability() -> None:
    """Test ClientInfo immutability."""
    client_info = ClientInfo()

    # Test that features list is immutable
    with pytest.raises(AttributeError):
        client_info.features.append("new_feature")

    # Test that other attributes are immutable
    with pytest.raises(AttributeError):
        client_info.name = "NewName"
