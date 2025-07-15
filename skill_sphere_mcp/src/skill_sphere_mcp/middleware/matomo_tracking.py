"""Matomo tracking middleware."""

import logging
import os

from typing import Awaitable
from typing import Callable
from typing import cast

import httpx

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


logger = logging.getLogger(__name__)

MATOMO_URL = os.getenv("MATOMO_URL", "http://matomo:80/matomo.php")
MATOMO_SITE_ID = os.getenv("MATOMO_SITE_ID", "1")
MATOMO_AUTH_TOKEN = os.getenv("MATOMO_AUTH_TOKEN", "")

class MatomoTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for Matomo analytics tracking."""

    def __init__(self, app: Callable) -> None:
        """Initialize the middleware."""
        super().__init__(app)
        self.client = httpx.AsyncClient()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatch the request with Matomo tracking."""
        # Process the request
        response = cast(Response, await call_next(request))
        
        # Track the request in Matomo (don't await to avoid blocking)
        # Use asyncio.create_task to run tracking in background
        import asyncio
        asyncio.create_task(self._track_request(request, response))
        
        return response

    async def _track_request(self, request: Request, response: Response) -> None:
        """Track the request in Matomo."""
        try:
            # Extract tracking parameters
            url = str(request.url)
            user_agent = request.headers.get("user-agent", "unknown")
            ip_address = request.client.host if request.client else "unknown"
            
            # Prepare tracking data
            tracking_data = {
                "idsite": "1",  # Matomo site ID
                "rec": "1",     # Record this hit
                "e_c": "MCP",   # Event category
                "e_a": request.url.path,  # Event action (URL path)
                "e_n": "unknown",  # Event name
                "e_v": "1",     # Event value
                "token_auth": "",  # Auth token (empty for now)
                "cip": ip_address,  # Client IP
                "ua": user_agent,   # User agent
            }
            
            # Send tracking request to Matomo
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://matomo/matomo.php",
                    params=tracking_data,
                    timeout=1.0  # Short timeout to not block the response
                )
                
        except Exception as e:
            # Log but don't fail the request
            logger.debug("Matomo tracking failed: %s", e)
