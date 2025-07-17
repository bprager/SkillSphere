"""JSON-RPC implementation for the MCP API."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from fastapi import HTTPException

logger = logging.getLogger(__name__)

# JSON-RPC error codes
ERROR_CODE_PARSE = -32700
ERROR_CODE_INVALID_REQUEST = -32600
ERROR_CODE_METHOD_NOT_FOUND = -32601
ERROR_CODE_INVALID_PARAMS = -32602
ERROR_CODE_INTERNAL = -32603

# HTTP Status Constants
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_BAD_REQUEST = 400

# Error message constants
ERROR_MSG_PARSE = "Parse error"
ERROR_MSG_INVALID_REQUEST = "Invalid request"
ERROR_MSG_METHOD_NOT_FOUND = "Method not found"
ERROR_MSG_INVALID_PARAMS = "Invalid params"
ERROR_MSG_INTERNAL = "Internal error"

# JSON-RPC Error Constants
ERROR_PARSE = {"code": ERROR_CODE_PARSE, "message": ERROR_MSG_PARSE}
ERROR_INVALID_REQUEST = {
    "code": ERROR_CODE_INVALID_REQUEST,
    "message": ERROR_MSG_INVALID_REQUEST,
}
ERROR_METHOD_NOT_FOUND = {
    "code": ERROR_CODE_METHOD_NOT_FOUND,
    "message": ERROR_MSG_METHOD_NOT_FOUND,
}
ERROR_INVALID_PARAMS = {
    "code": ERROR_CODE_INVALID_PARAMS,
    "message": ERROR_MSG_INVALID_PARAMS,
}
ERROR_INTERNAL = {"code": ERROR_CODE_INTERNAL, "message": ERROR_MSG_INTERNAL}

# Error messages
ERROR_MESSAGES = {
    "parse_error": ERROR_MSG_PARSE,
    "invalid_request": ERROR_MSG_INVALID_REQUEST,
    "method_not_found": ERROR_MSG_METHOD_NOT_FOUND,
    "invalid_params": ERROR_MSG_INVALID_PARAMS,
    "internal_error": ERROR_MSG_INTERNAL,
}

T = TypeVar("T")


def get_error_code(error_dict: dict[str, Any]) -> int:
    """Extract error code from error dictionary."""
    return int(error_dict["code"])


def get_error_message(error_dict: dict[str, Any]) -> str:
    """Extract error message from error dictionary."""
    return str(error_dict["message"])


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
        cls,
        code: int,
        message: str,
        request_id: str | int | None = None,
        data: Any = None,
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
        cls,
        error: Exception,
        request_id: str | int | None = None,
        is_validation_error: bool = False,
    ) -> "JSONRPCResponse":
        """Handle common error cases."""
        if isinstance(error, ValueError) or is_validation_error:
            return cls.create_error(ERROR_CODE_INVALID_PARAMS, str(error), request_id)
        return cls.create_error(
            ERROR_CODE_INTERNAL, "Internal server error", request_id
        )


def validate_jsonrpc_request(request: dict[str, Any]) -> bool:
    """Validate a JSON-RPC request."""
    if not isinstance(request, dict):
        raise HTTPException(
            status_code=HTTP_UNPROCESSABLE_ENTITY,
            detail="Request must be a JSON object",
        )

    if request.get("jsonrpc") != "2.0":
        raise HTTPException(
            status_code=HTTP_UNPROCESSABLE_ENTITY, detail="Invalid JSON-RPC version"
        )

    if "method" not in request:
        raise HTTPException(
            status_code=HTTP_UNPROCESSABLE_ENTITY, detail="Missing method"
        )

    if "params" in request and not isinstance(request["params"], dict):
        raise HTTPException(
            status_code=HTTP_UNPROCESSABLE_ENTITY, detail=ERROR_MSG_INVALID_PARAMS
        )

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


def handle_error(request_id: Any, error: Exception) -> dict[str, Any]:
    """Handle different types of errors and return appropriate JSON-RPC error response."""
    if isinstance(error, ValueError):
        return create_jsonrpc_error(ERROR_INVALID_PARAMS, request_id)
    if isinstance(error, HTTPException):
        if error.status_code == HTTP_UNPROCESSABLE_ENTITY:
            return create_jsonrpc_error(ERROR_INVALID_PARAMS, request_id)
        return create_jsonrpc_error(
            {"code": error.status_code, "message": error.detail}, request_id
        )
    return create_jsonrpc_error(ERROR_INTERNAL, request_id)


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
                ERROR_CODE_INVALID_REQUEST,
                ERROR_MESSAGES["invalid_request"],
                request.id,
            )

        if request.method not in self._methods:
            return JSONRPCResponse.create_error(
                ERROR_CODE_METHOD_NOT_FOUND,
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
                ERROR_CODE_INVALID_PARAMS,
                str(e),
                request.id,
            )
        except Exception as e:
            logger.error("Error handling request: %s", e)
            return JSONRPCResponse.create_error(
                ERROR_CODE_INTERNAL,
                ERROR_MESSAGES["internal_error"],
                request.id,
            )

    @staticmethod
    def create_error(code: int, message: str, data: Any = None) -> dict[str, Any]:
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
    def handle_error(error: Exception) -> dict[str, Any]:
        """Handle an error and create an appropriate response.

        Args:
            error: Exception to handle

        Returns:
            Error response dictionary
        """
        if isinstance(error, HTTPException):
            return JSONRPCResponse.create_error(
                ERROR_CODE_INVALID_PARAMS, str(error.detail)
            ).__dict__
        if isinstance(error, ValueError):
            return JSONRPCResponse.create_error(
                ERROR_CODE_INVALID_PARAMS, str(error)
            ).__dict__
        return JSONRPCResponse.create_error(
            ERROR_CODE_INTERNAL, ERROR_MESSAGES["internal_error"]
        ).__dict__
