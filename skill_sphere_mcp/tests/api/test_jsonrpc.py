"""Tests for JSON-RPC functionality."""

# pylint: disable=redefined-outer-name

import pytest
import pytest_asyncio
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_422_UNPROCESSABLE_ENTITY

from skill_sphere_mcp.api.jsonrpc import (
    ERROR_INVALID_PARAMS,
    ERROR_METHOD_NOT_FOUND,
    JSONRPCRequest,
    create_jsonrpc_error,
    create_jsonrpc_response,
    validate_jsonrpc_request,
)
from skill_sphere_mcp.app import app


@pytest_asyncio.fixture
async def jsonrpc_client():
    """Create a test client."""
    return TestClient(app)


def test_jsonrpc_request_validation():
    """Test JSON-RPC request validation."""
    # Valid request
    valid_request = {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": {"key": "value"},
        "id": 1,
    }
    assert validate_jsonrpc_request(valid_request) is True

    # Invalid JSON-RPC version
    invalid_version = {
        "jsonrpc": "1.0",
        "method": "test_method",
        "params": {"key": "value"},
        "id": 1,
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_jsonrpc_request(invalid_version)
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert "Invalid JSON-RPC version" in str(exc_info.value.detail)

    # Missing method
    missing_method = {"jsonrpc": "2.0", "params": {"key": "value"}, "id": 1}
    with pytest.raises(HTTPException) as exc_info:
        validate_jsonrpc_request(missing_method)
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert "Missing method" in str(exc_info.value.detail)

    # Invalid params type
    invalid_params = {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": "not_a_dict",
        "id": 1,
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_jsonrpc_request(invalid_params)
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert "Invalid params" in str(exc_info.value.detail)


def test_jsonrpc_response_creation():
    """Test JSON-RPC response creation."""
    # Success response
    result = {"data": "test"}
    response = create_jsonrpc_response(result, 1)
    assert response["jsonrpc"] == "2.0"
    assert response["result"] == result
    assert response["id"] == 1

    # Error response
    error = {"code": -32602, "message": "Invalid params"}
    response = create_jsonrpc_error(error, 1)
    assert response["jsonrpc"] == "2.0"
    assert response["error"] == error
    assert response["id"] == 1


def test_jsonrpc_request_model():
    """Test JSONRPCRequest model."""
    # Valid request
    request = JSONRPCRequest(
        jsonrpc="2.0", method="test_method", params={"key": "value"}, id=1
    )
    assert request.jsonrpc == "2.0"
    assert request.method == "test_method"
    assert request.params == {"key": "value"}
    assert request.id == 1

    # Test with optional params
    request = JSONRPCRequest(jsonrpc="2.0", method="test_method", id=1)
    assert request.params is None

    # Test with string ID
    request = JSONRPCRequest(jsonrpc="2.0", method="test_method", id="request-1")
    assert request.id == "request-1"


def test_jsonrpc_error_constants() -> None:
    """Test JSON-RPC error constants."""
    error_code_invalid_params = -32602
    error_code_method_not_found = -32601
    assert ERROR_INVALID_PARAMS["code"] == error_code_invalid_params
    assert ERROR_METHOD_NOT_FOUND["code"] == error_code_method_not_found
    assert "Invalid params" in ERROR_INVALID_PARAMS["message"]
    assert "Method not found" in ERROR_METHOD_NOT_FOUND["message"]


def test_rpc_endpoint_initialize(client: TestClient) -> None:
    """Test RPC initialize endpoint."""
    response = client.post(
        "/mcp/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "system.initialize",
            "params": {"protocol_version": "1.0", "client_info": {"name": "test"}},
            "id": 1,
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data or "error_data" in data
    assert data["id"] == 1


def test_rpc_endpoint_method_not_found(client: TestClient) -> None:
    """Test RPC endpoint with non-existent method."""
    response = client.post(
        "/mcp/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "system.nonexistent",
            "params": {},
            "id": 1,
        },
    )
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["error"]["code"] == ERROR_METHOD_NOT_FOUND["code"]
    assert data["id"] == 1
