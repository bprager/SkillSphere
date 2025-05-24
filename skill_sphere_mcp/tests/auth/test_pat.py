# pylint: disable=redefined-outer-name

"""Tests for PAT authentication."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from skill_sphere_mcp.auth.pat import PAT, PATAuth, get_current_token

HTTP_UNAUTHORIZED = 401


@pytest.fixture
def pat_auth() -> PATAuth:
    """Create a PAT auth instance for testing."""
    return PATAuth()


def test_create_token(pat_auth: PATAuth) -> None:
    """Test token creation."""
    pat = pat_auth.create_token("test token")
    assert isinstance(pat, PAT)
    assert pat.token.startswith("pat_")
    assert pat.description == "test token"
    assert pat.expires_at > datetime.now(timezone.utc)


def test_create_token_custom_expiry(pat_auth: PATAuth) -> None:
    """Test token creation with custom expiry."""
    pat = pat_auth.create_token("test token", expires_in_days=7)
    expected_expiry = datetime.now(timezone.utc) + timedelta(days=7)
    assert pat.expires_at > datetime.now(timezone.utc)
    assert pat.expires_at < expected_expiry + timedelta(minutes=1)


def test_create_multiple_tokens(pat_auth: PATAuth) -> None:
    """Test creating multiple tokens."""
    pat1 = pat_auth.create_token("token 1")
    pat2 = pat_auth.create_token("token 2")
    assert pat1.token != pat2.token
    assert pat_auth.validate_token(pat1.token) is True
    assert pat_auth.validate_token(pat2.token) is True


def test_validate_token(pat_auth: PATAuth) -> None:
    """Test token validation."""
    pat = pat_auth.create_token("test token")
    assert pat_auth.validate_token(pat.token) is True
    assert pat_auth.validate_token("invalid_token") is False


def test_validate_token_empty(pat_auth: PATAuth) -> None:
    """Test token validation with empty token."""
    assert pat_auth.validate_token("") is False


def test_revoke_token(pat_auth: PATAuth) -> None:
    """Test token revocation."""
    pat = pat_auth.create_token("test token")
    assert pat_auth.validate_token(pat.token) is True
    pat_auth.revoke_token(pat.token)
    assert pat_auth.validate_token(pat.token) is False


def test_revoke_nonexistent_token(pat_auth: PATAuth) -> None:
    """Test revoking a non-existent token."""
    pat_auth.revoke_token("nonexistent_token")  # Should not raise


def test_token_expiration(pat_auth: PATAuth) -> None:
    """Test token expiration."""
    pat = pat_auth.create_token("test token", expires_in_days=0)
    pat.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    assert pat_auth.validate_token(pat.token) is False


def test_token_expiration_edge_case(pat_auth: PATAuth) -> None:
    """Test token expiration edge case."""
    pat = pat_auth.create_token("test token")
    pat.expires_at = datetime.now(timezone.utc)  # Exactly now
    assert pat_auth.validate_token(pat.token) is False


@pytest.mark.asyncio
async def test_get_current_token(pat_auth: PATAuth) -> None:
    """Test get_current_token function."""
    with patch("skill_sphere_mcp.auth.pat.pat_auth", pat_auth):
        pat = pat_auth.create_token("test token")
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=pat.token
        )

        # Test valid token
        token = await get_current_token(credentials)
        assert token == pat.token

        # Test invalid token
        with pytest.raises(HTTPException) as exc_info:
            await get_current_token(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
            )
        assert exc_info.value.status_code == HTTP_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_token_expired(pat_auth: PATAuth) -> None:
    """Test get_current_token with expired token."""
    pat = pat_auth.create_token("test token", expires_in_days=0)
    pat.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=pat.token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_token(credentials)
    assert exc_info.value.status_code == HTTP_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_current_token_invalid_scheme(pat_auth: PATAuth) -> None:
    """Test get_current_token with invalid scheme."""
    pat = pat_auth.create_token("test token")
    credentials = HTTPAuthorizationCredentials(scheme="Basic", credentials=pat.token)

    with pytest.raises(HTTPException) as exc_info:
        await get_current_token(credentials)
    assert exc_info.value.status_code == HTTP_UNAUTHORIZED
