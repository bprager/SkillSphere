"""Personal Access Token (PAT) authentication."""

import logging
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

logger = logging.getLogger(__name__)

security = HTTPBearer()
get_credentials = Depends(security)


class PAT(BaseModel):
    """Personal Access Token model."""

    token: str
    expires_at: datetime
    description: str


class PATAuth:
    """PAT authentication handler."""

    def __init__(self) -> None:
        """Initialize PAT authentication."""
        self._tokens: dict[str, PAT] = {}

    def create_token(self, description: str, expires_in_days: int = 30) -> PAT:
        """Create a new PAT.

        Args:
            description: Token description
            expires_in_days: Token validity in days

        Returns:
            New PAT instance
        """
        # Generate a random token (in production, use a proper token generator)
        token = f"pat_{datetime.now(timezone.utc).timestamp()}"
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        pat = PAT(token=token, expires_at=expires_at, description=description)
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
        if token not in self._tokens:
            return False

        pat = self._tokens[token]
        if datetime.now(timezone.utc) > pat.expires_at:
            del self._tokens[token]
            return False

        return True

    def revoke_token(self, token: str) -> None:
        """Revoke a PAT.

        Args:
            token: Token to revoke
        """
        if token in self._tokens:
            del self._tokens[token]
            logger.info("Revoked PAT")


# Global PAT auth instance
pat_auth = PATAuth()


async def get_current_token(
    credentials: HTTPAuthorizationCredentials = get_credentials,
) -> str:
    """Get and validate the current PAT.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Valid token string

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    if not pat_auth.validate_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token
