"""Personal Access Token (PAT) authentication."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# HTTP status codes
HTTP_UNAUTHORIZED = 401

# Security scheme
security = HTTPBearer()


class PAT(BaseModel):
    """Personal Access Token model."""

    token: str
    description: str
    expires_at: datetime


class PATAuth:
    """Personal Access Token authentication manager."""

    def __init__(self) -> None:
        """Initialize the PAT auth manager."""
        self._tokens: dict[str, PAT] = {}

    def create_token(self, description: str, expires_in_days: int = 30) -> PAT:
        """Create a new PAT.

        Args:
            description: Token description
            expires_in_days: Token expiration time in days (default: 30)

        Returns:
            PAT object
        """
        token = f"pat_{uuid4()}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        pat = PAT(token=token, description=description, expires_at=expires_at)
        self._tokens[token] = pat
        return pat

    def validate_token(self, token: str) -> bool:
        """Validate a PAT.

        Args:
            token: Token to validate

        Returns:
            True if token is valid, False otherwise
        """
        if not token or token not in self._tokens:
            return False
        pat = self._tokens[token]
        if pat.expires_at < datetime.now(timezone.utc):
            del self._tokens[token]
            return False
        return True

    def revoke_token(self, token: str) -> None:
        """Revoke a PAT.

        Args:
            token: Token to revoke
        """
        self._tokens.pop(token, None)


# Global PAT auth instance
pat_auth = PATAuth()


async def get_current_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
) -> str:
    """Get the current token from the request.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Token string

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    if not pat_auth.validate_token(token):
        raise HTTPException(
            status_code=HTTP_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return str(token)


async def verify_pat(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
) -> str:
    """Verify PAT authentication.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Token string if valid

    Raises:
        HTTPException: If token is invalid or expired
    """
    return await get_current_token(credentials)
