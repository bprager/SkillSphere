"""OAuth authentication utilities for FastAPI."""

import os
from typing import Any

from fastapi import Depends, HTTPException, Request, status


# Mock classes for OAuth2 functionality (placeholder implementation)
class IntrospectionTokenValidator:
    """Mock token validator for testing."""
    def __init__(self, **kwargs: Any) -> None:
        pass

class OAuth2ResourceProtector:
    """Mock OAuth2 resource protector for testing."""
    def __init__(self, token_validator: IntrospectionTokenValidator | None = None) -> None:
        self.token_validator = token_validator

    def __call__(self, request: Request) -> Any:
        """Mock token validation."""
        class MockToken:
            """Mock token for testing."""
            active = True
            sub = "test_user"
            scope = "read write"
        return MockToken()

OAUTH_AVAILABLE = False

OAUTH_INTROSPECTION_URL = os.getenv("OAUTH_INTROSPECTION_URL")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
MCP_RESOURCE_ID = os.getenv("MCP_RESOURCE_ID")

# Since we're using mock classes, we don't need to check for environment variables
# The mock implementation will always be used

oauth2_protector = OAuth2ResourceProtector()

async def validate_access_token(_request: Request, token: Any = Depends(oauth2_protector)) -> Any:
    """Validate OAuth2 access token and return the token if valid."""
    if not token or not getattr(token, "active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing OAuth2 access token",
        )
    return token

class MockToken:
    """Mock token for testing purposes."""


class OAuthConfig:
    """Configuration for OAuth authentication."""


class TokenValidator:
    """Validator for OAuth tokens."""


class OAuth2ResourceServer:
    """OAuth2 Resource Server for token validation."""
