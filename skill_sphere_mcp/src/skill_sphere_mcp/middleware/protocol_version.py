from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

MCP_PROTOCOL_VERSION = "2025-06-18"

class ProtocolVersionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        version = request.headers.get("MCP-Protocol-Version")
        if version != MCP_PROTOCOL_VERSION:
            return JSONResponse(
                status_code=426,
                content={"required_version": MCP_PROTOCOL_VERSION},
            )
        response = await call_next(request)
        response.headers["MCP-Protocol-Version"] = MCP_PROTOCOL_VERSION
        return response
