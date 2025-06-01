"""JSON-RPC implementation for the MCP API."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

# Error codes
ERROR_PARSE = -32700
ERROR_INVALID_REQUEST = -32600
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602
ERROR_INTERNAL = -32603

T = TypeVar("T")


@dataclass
class JSONRPCRequest:
    """JSON-RPC request."""

    method: str
    jsonrpc: str = "2.0"
    params: dict[str, Any] = None
    id: str | int | None = None

    def __post_init__(self) -> None:
        """Validate request fields."""
        if self.params is None:
            self.params = {}
        if self.jsonrpc != "2.0":
            raise ValueError("Invalid JSON-RPC version")
        if not self.method:
            raise ValueError("Method is required")
        if not isinstance(self.params, dict):
            raise ValueError("Params must be a dictionary")


@dataclass
class JSONRPCError:
    """JSON-RPC error."""

    code: int
    message: str
    data: Any | None = None


@dataclass
class JSONRPCResponse:
    """JSON-RPC response."""

    jsonrpc: str = "2.0"
    result: Any | None = None
    error: dict[str, Any] | None = None
    id: str | int | None = None

    @classmethod
    def success(cls, result: Any, request_id: str | int | None) -> "JSONRPCResponse":
        """Create a success response."""
        return cls(result=result, id=request_id)

    @classmethod
    def create_error(
        cls,
        code: int,
        message: str,
        request_id: str | int | None,
        data: Any | None = None,
    ) -> "JSONRPCResponse":
        """Create an error response."""
        return cls(
            error={"code": code, "message": message, "data": data}, id=request_id
        )

    @classmethod
    def handle_error(
        cls,
        error: Exception,
        request_id: str | int | None,
        is_validation_error: bool = False,
    ) -> "JSONRPCResponse":
        """Handle common error cases."""
        if isinstance(error, ValueError) or is_validation_error:
            return cls.create_error(ERROR_INVALID_PARAMS, str(error), request_id)
        return cls.create_error(ERROR_INTERNAL, str(error), request_id)


class JSONRPCHandler:
    """JSON-RPC request handler."""

    def __init__(self) -> None:
        """Initialize the handler."""
        self._methods: dict[str, Callable[..., Any]] = {}

    def register(self, method: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Register a method handler."""

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            self._methods[method] = func
            return func

        return decorator

    async def handle_request(
        self, request: JSONRPCRequest, session: Any | None = None
    ) -> JSONRPCResponse:
        """Handle a JSON-RPC request."""
        if request.jsonrpc != "2.0":
            return JSONRPCResponse.create_error(
                ERROR_INVALID_REQUEST,
                "Invalid JSON-RPC version",
                request.id,
            )

        if request.method not in self._methods:
            return JSONRPCResponse.create_error(
                ERROR_METHOD_NOT_FOUND,
                f"Method not found: {request.method}",
                request.id,
            )

        try:
            handler = self._methods[request.method]
            if session is not None:
                result = await handler(request.params, session)
            else:
                result = await handler(request.params)
            return JSONRPCResponse.success(result, request.id)
        except (ValueError, RuntimeError, TypeError) as e:
            return JSONRPCResponse.handle_error(e, request.id)
