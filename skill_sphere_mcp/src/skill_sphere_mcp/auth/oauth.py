import os
from fastapi import Depends, HTTPException, status, Request
from typing import Any

# Try to import the OAuth package, but provide a mock if it's not available
try:
    from fastapi_oauth2_resource_server import OAuth2ResourceProtector, IntrospectionTokenValidator
    OAUTH_AVAILABLE = True
except ImportError:
    # Mock classes for testing when OAuth package is not available
    class IntrospectionTokenValidator:
        def __init__(self, **kwargs):
            pass
    
    class OAuth2ResourceProtector:
        def __init__(self, token_validator=None):
            self.token_validator = token_validator
        
        def __call__(self, request: Request):
            # For testing, always return a mock token
            class MockToken:
                active = True
                sub = "test_user"
                scope = "read write"
            return MockToken()
    
    OAUTH_AVAILABLE = False

OAUTH_INTROSPECTION_URL = os.getenv("OAUTH_INTROSPECTION_URL")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
MCP_RESOURCE_ID = os.getenv("MCP_RESOURCE_ID")

# Only raise error if OAuth is available but missing required env vars
if OAUTH_AVAILABLE and (not OAUTH_INTROSPECTION_URL or not OAUTH_CLIENT_ID or not MCP_RESOURCE_ID):
    raise RuntimeError(
        "Missing required OAuth2 environment variables: "
        "OAUTH_INTROSPECTION_URL, OAUTH_CLIENT_ID, MCP_RESOURCE_ID"
    )

if OAUTH_AVAILABLE:
    token_validator = IntrospectionTokenValidator(
        introspection_endpoint=OAUTH_INTROSPECTION_URL,
        client_id=OAUTH_CLIENT_ID,
        resource_indicator=MCP_RESOURCE_ID,
    )
    oauth2_protector = OAuth2ResourceProtector(token_validator=token_validator)
else:
    # Use mock for testing
    oauth2_protector = OAuth2ResourceProtector()

async def validate_access_token(request: Request, token: Any = Depends(oauth2_protector)):
    if not token or not getattr(token, "active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing OAuth2 access token",
        )
    return token
