"""JSON-RPC implementation for the MCP API."""

import logging

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import Optional
from typing import TypeVar

from fastapi import HTTPException
from neo4j import AsyncSession

from ..api.mcp.handlers import handle_search
from ..api.mcp.handlers import handle_tool_dispatch


logger = logging.getLogger(__name__)

# JSON-RPC error constants
ERROR_PARSE = {"code": -32700, "message": "Parse error"}
ERROR_INVALID_REQUEST = {"code": -32600, "message": "Invalid request"}
ERROR_METHOD_NOT_FOUND = {"code": -32601, "message": "Method not found"}
ERROR_INVALID_PARAMS = {"code": -32602, "message": "Invalid params"}
ERROR_INTERNAL = {"code": -32603, "message": "Internal error"}

# Error messages
ERROR_MESSAGES = {
    "parse_error": "Parse error",
    "invalid_request": "Invalid request",
    "method_not_found": "Method not found",
    "invalid_params": "Invalid params",
    "internal_error": "Internal error",
}

T = TypeVar("T")


@dataclass
class JSONRPCRequest:
    """JSON-RPC request."""

    method: str
    jsonrpc: str = "2.0"
    params: dict[str, Any] | None = None
    id: str | int | None = None

    def __post_init__(self) -> None:
        """Validate request fields."""
        if self.jsonrpc != "2.0":
            raise HTTPException(status_code=422, detail="Invalid JSON-RPC version")
        if not self.method:
            raise HTTPException(status_code=422, detail="Method is required")
        if self.params is not None and not isinstance(self.params, dict):
            raise HTTPException(status_code=422, detail="Params must be a dictionary")


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
        cls, code: int, message: str, request_id: Optional[int] = None, data: Any = None
    ) -> "JSONRPCResponse":
        """Create an error response."""
        error = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return cls(
            jsonrpc="2.0",
            error=error,
            id=request_id,
        )

    @classmethod
    def handle_error(
        cls, error: Exception, request_id: Optional[int] = None, is_validation_error: bool = False
    ) -> "JSONRPCResponse":
        """Handle common error cases."""
        if isinstance(error, ValueError) or is_validation_error:
            return cls.create_error(ERROR_INVALID_PARAMS["code"], str(error), request_id)
        return cls.create_error(ERROR_INTERNAL["code"], "Internal server error", request_id)


def validate_jsonrpc_request(request: dict[str, Any]) -> bool:
    """Validate a JSON-RPC request."""
    if not isinstance(request, dict):
        raise HTTPException(status_code=422, detail="Request must be a JSON object")

    if request.get("jsonrpc") != "2.0":
        raise HTTPException(status_code=422, detail="Invalid JSON-RPC version")

    if "method" not in request:
        raise HTTPException(status_code=422, detail="Missing method")

    if "params" in request and not isinstance(request["params"], dict):
        raise HTTPException(status_code=422, detail="Invalid params")

    return True


def create_jsonrpc_response(result: Any, request_id: Any) -> dict[str, Any]:
    """Create a JSON-RPC success response."""
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": request_id,
    }


def create_jsonrpc_error(error: dict, request_id: Any) -> dict[str, Any]:
    """Create a JSON-RPC error response."""
    return {
        "jsonrpc": "2.0",
        "error": error,
        "id": request_id,
    }


def create_error(code: int, message: str, data: Any = None) -> dict[str, Any]:
    """Create a JSON-RPC error response."""
    error = {
        "code": code,
        "message": message,
    }
    if data is not None:
        error["data"] = data
    return error


async def handle_error(request_id: Any, error: Exception) -> dict[str, Any]:
    """Handle different types of errors and return appropriate JSON-RPC error response."""
    if isinstance(error, ValueError):
        return create_jsonrpc_error(ERROR_INVALID_PARAMS, request_id)
    if isinstance(error, HTTPException):
        if error.status_code == 422:
            return create_jsonrpc_error(ERROR_INVALID_PARAMS, request_id)
        return create_jsonrpc_error(
            {"code": error.status_code, "message": error.detail}, request_id
        )
    return create_jsonrpc_error(ERROR_INTERNAL, request_id)


async def handle_request(request: JSONRPCRequest, session: AsyncSession) -> dict[str, Any]:
    """Handle JSON-RPC request.

    Args:
        request: JSON-RPC request
        session: Database session

    Returns:
        JSON-RPC response
    """
    # Reject batch requests (list of requests)
    if isinstance(request, list):
        return create_jsonrpc_error(
            {"code": -32600, "message": "Batch requests are not supported"},
            None,
        )

    # Validate request
    if not request.jsonrpc or request.jsonrpc != "2.0":
        return create_jsonrpc_error(ERROR_INVALID_REQUEST, request.id)

    # Handle method
    if request.method == "mcp.search":
        if not request.params or "query" not in request.params:
            return create_jsonrpc_error(
                {"code": ERROR_INVALID_PARAMS["code"], "message": "Query is required"}, request.id
            )
        try:
            result = await handle_search(
                session, request.params["query"], request.params.get("limit", 10)
            )
            return create_jsonrpc_response(result, request.id)
        except Exception as e:
            return await handle_error(request.id, e)
    elif request.method == "mcp.tool":
        if not request.params or "tool_name" not in request.params:
            return create_jsonrpc_error(
                {"code": ERROR_INVALID_PARAMS["code"], "message": "Tool name is required"}, request.id
            )
        try:
            result = await handle_tool_dispatch(
                session, request.params["tool_name"], request.params.get("parameters", {})
            )
            return create_jsonrpc_response(result, request.id)
        except Exception as e:
            return await handle_error(request.id, e)
    else:
        return create_jsonrpc_error(
            {"code": ERROR_METHOD_NOT_FOUND["code"], "message": f"Unknown method: {request.method}"},
            request.id,
        )


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
                ERROR_INVALID_REQUEST["code"],
                ERROR_MESSAGES["invalid_request"],
                request.id,
            )

        if request.method not in self._methods:
            return JSONRPCResponse.create_error(
                ERROR_METHOD_NOT_FOUND["code"],
                ERROR_MESSAGES["method_not_found"],
                request.id,
            )

        try:
            handler = self._methods[request.method]
            if session is not None:
                result = await handler(request.params, session)
            else:
                result = await handler(request.params)
            return JSONRPCResponse.success(result, request.id)
        except ValueError as e:
            return JSONRPCResponse.create_error(
                ERROR_INVALID_PARAMS["code"],
                str(e),
                request.id,
            )
        except Exception as e:
            logger.error("Error handling request: %s", e)
            return JSONRPCResponse.create_error(
                ERROR_INTERNAL["code"],
                ERROR_MESSAGES["internal_error"],
                request.id,
            )

    @staticmethod
    def create_error(code: int, message: str, data: Any = None) -> dict:
        """Create an error response.

        Args:
            code: Error code
            message: Error message
            data: Additional error data

        Returns:
            Error response dictionary
        """
        error = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        return error

    @staticmethod
    def handle_error(error: Exception) -> dict:
        """Handle an error and create an appropriate response.

        Args:
            error: Exception to handle

        Returns:
            Error response dictionary
        """
        if isinstance(error, HTTPException):
            return JSONRPCResponse.create_error(
                ERROR_INVALID_PARAMS["code"], str(error.detail)
            )
        if isinstance(error, ValueError):
            return JSONRPCResponse.create_error(ERROR_INVALID_PARAMS["code"], str(error))
        return JSONRPCResponse.create_error(
            ERROR_INTERNAL["code"], ERROR_MESSAGES["internal_error"]
        )
