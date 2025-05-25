"""JSON-RPC 2.0 request/response handling."""

import logging
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field, model_validator

logger = logging.getLogger(__name__)

# JSON-RPC 2.0 error codes
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602
ERROR_INTERNAL = -32603


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request model."""

    jsonrpc: str = Field(default="2.0")
    method: str = Field(pattern=r".+\..+")
    params: dict[str, Any] | None = None
    id: int | str | None = None

    model_config = {"validate_assignment": True, "extra": "forbid"}

    @model_validator(mode="after")
    def validate_method(self) -> "JSONRPCRequest":
        """Validate the request after initialization."""
        if not self.method:
            raise ValueError("method cannot be empty")
        return self


class JSONRPCResponse(BaseModel):
    """JSON-RPC response model."""

    jsonrpc: str = "2.0"
    result: Any | None = None
    error_data: dict[str, Any] | None = None
    id: int | str | None = None

    @classmethod
    def success(cls, result: Any, request_id: int | str | None) -> "JSONRPCResponse":
        """Create a success response."""
        return cls(result=result, id=request_id)

    @classmethod
    def error(
        cls,
        code: int,
        message: str,
        request_id: int | str | None,
    ) -> "JSONRPCResponse":
        """Create an error response."""
        return cls(
            error_data={"code": code, "message": message},
            id=request_id,
        )


class JSONRPCHandler:
    """JSON-RPC 2.0 request handler."""

    def __init__(self) -> None:
        """Initialize the handler."""
        self._methods: dict[str, Callable] = {}

    def register(self, method: str) -> Callable:
        """Register a method handler."""

        def decorator(func: Callable) -> Callable:
            self._methods[method] = func
            return func

        return decorator

    async def handle_request(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle a JSON-RPC request.

        Args:
            request: The JSON-RPC request to handle

        Returns:
            JSON-RPC response

        Raises:
            HTTPException: If request is invalid
        """
        if request.jsonrpc != "2.0":
            return JSONRPCResponse(
                jsonrpc="2.0",
                error_data={
                    "code": ERROR_INVALID_REQUEST,
                    "message": f"Invalid JSON-RPC version: {request.jsonrpc}",
                },
                id=request.id,
            )

        if not request.method:
            return JSONRPCResponse(
                jsonrpc="2.0",
                error_data={
                    "code": ERROR_INVALID_REQUEST,
                    "message": "Method is required",
                },
                id=request.id,
            )

        handler = self._methods.get(request.method)
        if not handler:
            return JSONRPCResponse(
                jsonrpc="2.0",
                error_data={
                    "code": ERROR_METHOD_NOT_FOUND,
                    "message": f"Method {request.method} not found",
                },
                id=request.id,
            )

        try:
            result = await handler(request.params or {})
            return JSONRPCResponse(jsonrpc="2.0", result=result, id=request.id)
        except (TypeError, ValueError, KeyError, RuntimeError) as e:
            logger.exception("Error handling request")
            return JSONRPCResponse(
                jsonrpc="2.0",
                error_data={"code": ERROR_INTERNAL, "message": str(e)},
                id=request.id,
            )
