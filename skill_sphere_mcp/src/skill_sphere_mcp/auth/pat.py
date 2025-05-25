"""Personal Access Token (PAT) authentication."""

import logging
from datetime import datetime, timedelta, timezone
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
    created_at: datetime
    expires_at: datetime


class PATAuth:
    """PAT authentication manager."""

    def __init__(self) -> None:
        """Initialize PAT auth manager."""
        self._tokens: dict[str, PAT] = {}

    def create_token(self, description: str, expires_in_days: int = 30) -> PAT:
        """Create a new PAT.

        Args:
            description: Token description
            expires_in_days: Days until token expires

        Returns:
            Created PAT
        """
        token = f"pat_{uuid4().hex}"
        now = datetime.now(timezone.utc)
        pat = PAT(
            token=token,
            description=description,
            created_at=now,
            expires_at=now + timedelta(days=expires_in_days),
        )
        self._tokens[token] = pat
        logger.info("Created new PAT: %s", description)
        return pat

    def validate_token(self, token: str) -> bool:
        """Validate a PAT.

        Args:
            token: Token to validate

        Returns:
            True if token is valid
        """
        if not token:
            return False
        pat = self._tokens.get(token)
        if not pat:
            return False
        if pat.expires_at <= datetime.now(timezone.utc):
            del self._tokens[token]
            return False
        return True

    def revoke_token(self, token: str) -> None:
        """Revoke a PAT.

        Args:
            token: Token to revoke
        """
        self._tokens.pop(token, None)
        logger.info("Revoked PAT")


# Global PAT auth instance
pat_auth = PATAuth()


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """Get current PAT from request.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Valid PAT

    Raises:
        HTTPException: If token is invalid
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=HTTP_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    token = credentials.credentials
    if not pat_auth.validate_token(token):
        raise HTTPException(
            status_code=HTTP_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return token


async def verify_pat(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> None:
    """Verify PAT authentication.

    Args:
        credentials: HTTP authorization credentials

    Raises:
        HTTPException: If token is invalid
    """
    await get_current_token(credentials)
