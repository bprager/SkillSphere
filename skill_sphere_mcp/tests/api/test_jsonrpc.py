"""Tests for JSON-RPC functionality."""

# pylint: disable=redefined-outer-name

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from skill_sphere_mcp.api.jsonrpc import (ERROR_INVALID_REQUEST,
                                          ERROR_METHOD_NOT_FOUND,
                                          JSONRPCRequest, JSONRPCResponse)
from skill_sphere_mcp.app import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client."""
    return TestClient(app)


def test_jsonrpc_request_validation() -> None:
    """Test JSON-RPC request validation."""
    # Valid request
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="test.method",
        params={"key": "value"},
        id=1,
    )
    assert request.jsonrpc == "2.0"
    assert request.method == "test.method"
    assert request.params == {"key": "value"}
    assert request.id == 1

    # Invalid jsonrpc version
    with pytest.raises(ValueError):
        JSONRPCRequest(jsonrpc="1.0", method="test")

    # Missing method
    with pytest.raises(ValueError):
        JSONRPCRequest(method="", id=1)


def test_jsonrpc_response_creation() -> None:
    """Test JSON-RPC response creation."""
    # Success response
    response = JSONRPCResponse(
        jsonrpc="2.0",
        result={"key": "value"},
        id=1,
    )
    assert response.jsonrpc == "2.0"
    assert response.result == {"key": "value"}
    assert response.id == 1

    # Error response
    error_response = JSONRPCResponse(
        jsonrpc="2.0",
        error_data={"code": ERROR_INVALID_REQUEST, "message": "Invalid request"},
        id=1,
    )
    assert error_response.jsonrpc == "2.0"
    assert error_response.error_data == {
        "code": ERROR_INVALID_REQUEST,
        "message": "Invalid request",
    }
    assert error_response.id == 1


def test_rpc_endpoint_initialize(test_client: TestClient) -> None:
    """Test RPC initialize endpoint."""
    response = test_client.post(
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


def test_rpc_endpoint_method_not_found(test_client: TestClient) -> None:
    """Test RPC endpoint with non-existent method."""
    response = test_client.post(
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
    assert "error_data" in data
    assert data["error_data"]["code"] == ERROR_METHOD_NOT_FOUND
    assert data["id"] == 1
