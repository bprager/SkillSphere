# pylint: disable=redefined-outer-name

"""Tests for Personal Access Token (PAT) authentication."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from skill_sphere_mcp.auth.pat import (
    PAT,
    PATAuth,
    get_current_token,
    pat_auth,
    verify_pat,
)

HTTP_UNAUTHORIZED = 401


@pytest.fixture
def auth_manager():
    """Create a fresh PAT auth manager for each test."""
    return PATAuth()


@pytest.fixture
def mock_credentials():
    """Create mock HTTP authorization credentials."""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="test_token")


def test_create_token(auth_manager):
    """Test token creation."""
    # Create a token
    pat = auth_manager.create_token("Test token")

    # Verify token structure
    assert pat.token.startswith("pat_")
    assert pat.description == "Test token"
    assert isinstance(pat.expires_at, datetime)
    assert pat.expires_at > datetime.now(timezone.utc)

    # Verify token is stored
    assert pat.token in auth_manager._tokens
    assert auth_manager._tokens[pat.token] == pat


def test_create_token_custom_expiry(auth_manager):
    """Test token creation with custom expiry."""
    # Create a token with 7 days expiry
    pat = auth_manager.create_token("Test token", expires_in_days=7)

    # Verify expiry
    expected_expiry = datetime.now(timezone.utc) + timedelta(days=7)
    assert abs((pat.expires_at - expected_expiry).total_seconds()) < 1


def test_create_multiple_tokens(auth_manager):
    """Test creating multiple tokens."""
    pat1 = auth_manager.create_token("token 1")
    pat2 = auth_manager.create_token("token 2")
    assert pat1.token != pat2.token
    assert auth_manager.validate_token(pat1.token) is True
    assert auth_manager.validate_token(pat2.token) is True


def test_validate_token_valid(auth_manager):
    """Test validation of valid token."""
    # Create a token
    pat = auth_manager.create_token("Test token")

    # Verify token is valid
    assert auth_manager.validate_token(pat.token) is True


def test_validate_token_invalid(auth_manager):
    """Test validation of invalid token."""
    # Verify non-existent token is invalid
    assert auth_manager.validate_token("invalid_token") is False


def test_validate_token_expired(auth_manager):
    """Test validation of expired token."""
    # Create a token with immediate expiry
    pat = auth_manager.create_token("Test token", expires_in_days=0)
    pat.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    auth_manager._tokens[pat.token] = pat

    # Verify expired token is invalid
    assert auth_manager.validate_token(pat.token) is False
    # Verify expired token is removed
    assert pat.token not in auth_manager._tokens


def test_revoke_token(auth_manager):
    """Test token revocation."""
    # Create a token
    pat = auth_manager.create_token("Test token")

    # Revoke token
    auth_manager.revoke_token(pat.token)

    # Verify token is removed
    assert pat.token not in auth_manager._tokens
    assert auth_manager.validate_token(pat.token) is False


def test_revoke_nonexistent_token(auth_manager):
    """Test revocation of non-existent token."""
    # Revoke non-existent token
    auth_manager.revoke_token("nonexistent_token")
    # Should not raise any exception


def test_token_expiration(auth_manager):
    """Test token expiration."""
    pat = auth_manager.create_token("Test token", expires_in_days=0)
    pat.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    assert auth_manager.validate_token(pat.token) is False


def test_token_expiration_edge_case(auth_manager):
    """Test token expiration edge case."""
    pat = auth_manager.create_token("Test token")
    pat.expires_at = datetime.now(timezone.utc)
    assert auth_manager.validate_token(pat.token) is False


@pytest.mark.asyncio
async def test_get_current_token_valid(mock_credentials):
    """Test getting current token with valid credentials."""
    # Create a valid token using the global pat_auth
    pat = pat_auth.create_token("Test token")
    mock_credentials.credentials = pat.token

    # Get current token
    token = await get_current_token(mock_credentials)

    # Verify token
    assert token == pat.token


@pytest.mark.asyncio
async def test_get_current_token_invalid(mock_credentials):
    """Test getting current token with invalid credentials."""
    # Set invalid token
    mock_credentials.credentials = "invalid_token"

    # Verify exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await get_current_token(mock_credentials)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or expired token"
    # Only check headers if present (pyright: Object of type None is not subscriptable)
    if exc_info.value.headers is not None:
        assert exc_info.value.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.asyncio
async def test_get_current_token_expired(mock_credentials):
    """Test getting current token with expired credentials."""
    # Create and expire a token using the global pat_auth
    pat = pat_auth.create_token("Test token")
    pat.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    pat_auth._tokens[pat.token] = pat
    mock_credentials.credentials = pat.token

    # Verify exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await get_current_token(mock_credentials)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or expired token"


@pytest.mark.asyncio
async def test_verify_pat_valid(mock_credentials):
    """Test PAT verification with valid token."""
    # Create a valid token using the global pat_auth
    pat = pat_auth.create_token("Test token")
    mock_credentials.credentials = pat.token

    # Verify PAT
    token = await verify_pat(mock_credentials)

    # Verify token
    assert token == pat.token


@pytest.mark.asyncio
async def test_verify_pat_invalid(mock_credentials):
    """Test PAT verification with invalid token."""
    # Set invalid token
    mock_credentials.credentials = "invalid_token"

    # Verify exception is raised
    with pytest.raises(HTTPException) as exc_info:
        await verify_pat(mock_credentials)

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid or expired token"


def test_pat_model_validation():
    """Test PAT model validation."""
    # Valid PAT
    pat = PAT(
        token="pat_123",
        description="Test token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    assert pat.token == "pat_123"
    assert pat.description == "Test token"

    # Invalid PAT (missing required fields)
    with pytest.raises(ValueError):
        PAT(token="pat_123")  # Missing description and expires_at
