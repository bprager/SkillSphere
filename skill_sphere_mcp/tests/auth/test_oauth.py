import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from fastapi import HTTPException
from fastapi.requests import Request

# Import the module under test
import skill_sphere_mcp.auth.oauth as oauth_module


def test_runtime_error_on_missing_env_vars(monkeypatch):
    # Skip this test if the OAuth dependency is not available (mocked)
    if not getattr(oauth_module, "OAUTH_AVAILABLE", True):
        pytest.skip("fastapi_oauth2_resource_server not installed; skipping env var RuntimeError test.")

    # Clear environment variables
    monkeypatch.delenv("OAUTH_INTROSPECTION_URL", raising=False)
    monkeypatch.delenv("OAUTH_CLIENT_ID", raising=False)
    monkeypatch.delenv("MCP_RESOURCE_ID", raising=False)

    # Reload the module to trigger environment variable check
    with pytest.raises(RuntimeError) as exc_info:
        # We need to reload the module to re-run the top-level code
        import importlib
        importlib.reload(oauth_module)

    assert "Missing required OAuth2 environment variables" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_access_token_raises_http_exception_if_token_missing_or_inactive():
    # Create a mock request (not used in function but required by signature)
    mock_request = MagicMock(spec=Request)

    # Case 1: token is None
    with pytest.raises(HTTPException) as exc_info:
        await oauth_module.validate_access_token(mock_request, token=None)
    assert exc_info.value.status_code == 401
    assert "Invalid or missing OAuth2 access token" in exc_info.value.detail

    # Case 2: token.active is False
    mock_token = MagicMock()
    mock_token.active = False
    with pytest.raises(HTTPException) as exc_info:
        await oauth_module.validate_access_token(mock_request, token=mock_token)
    assert exc_info.value.status_code == 401
    assert "Invalid or missing OAuth2 access token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_validate_access_token_returns_token_if_active():
    mock_request = MagicMock(spec=Request)
    mock_token = MagicMock()
    mock_token.active = True

    result = await oauth_module.validate_access_token(mock_request, token=mock_token)
    assert result == mock_token
