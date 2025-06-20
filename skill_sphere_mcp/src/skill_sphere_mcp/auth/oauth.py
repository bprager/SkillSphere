import os
from fastapi import Depends, HTTPException, status, Request
from fastapi_oauth2_resource_server import OAuth2ResourceProtector, IntrospectionTokenValidator
from typing import Any

OAUTH_INTROSPECTION_URL = os.getenv("OAUTH_INTROSPECTION_URL")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
MCP_RESOURCE_ID = os.getenv("MCP_RESOURCE_ID")

if not OAUTH_INTROSPECTION_URL or not OAUTH_CLIENT_ID or not MCP_RESOURCE_ID:
    raise RuntimeError(
        "Missing required OAuth2 environment variables: "
        "OAUTH_INTROSPECTION_URL, OAUTH_CLIENT_ID, MCP_RESOURCE_ID"
    )

token_validator = IntrospectionTokenValidator(
    introspection_endpoint=OAUTH_INTROSPECTION_URL,
    client_id=OAUTH_CLIENT_ID,
    resource_indicator=MCP_RESOURCE_ID,
)

oauth2_protector = OAuth2ResourceProtector(token_validator=token_validator)

async def validate_access_token(request: Request, token: Any = Depends(oauth2_protector)):
    if not token or not getattr(token, "active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing OAuth2 access token",
        )
    return token
