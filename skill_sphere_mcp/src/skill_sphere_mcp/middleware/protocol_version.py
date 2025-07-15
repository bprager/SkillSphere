"""Protocol version middleware."""

from typing import Callable
from typing import cast

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.types import ASGIApp


MCP_PROTOCOL_VERSION = "2025-06-18"

class ProtocolVersionMiddleware(BaseHTTPMiddleware):
    """Middleware to check protocol version."""

    def __init__(self, app: Callable, required_version: str = MCP_PROTOCOL_VERSION) -> None:
        """Initialize the middleware."""
        super().__init__(app)
        self.required_version = required_version

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Dispatch the request with protocol version check."""
        # Check if the request has the required protocol version
        protocol_version = request.headers.get("MCP-Protocol-Version")
        
        if protocol_version and protocol_version != self.required_version:
            return JSONResponse(
                content=f"Unsupported protocol version: {protocol_version}",
                status_code=400
            )
        
        response = cast(Response, await call_next(request))
        response.headers["MCP-Protocol-Version"] = self.required_version
        return response
