"""Tests for the MCP server."""

from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from neo4j import AsyncSession

from skill_sphere_mcp.api.jsonrpc import (ERROR_INVALID_PARAMS,
                                          ERROR_METHOD_NOT_FOUND,
                                          JSONRPCRequest)


@pytest.mark.asyncio
async def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/v1/healthz")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_entity_not_found(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test getting a non-existent entity."""
    mock_neo4j_session.run.return_value.single.return_value = None
    response = client.get("/mcp/entities/nonexistent")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Entity not found"}


@pytest.mark.asyncio
async def test_search_success(
    client: TestClient,
    mock_neo4j_session: AsyncSession,
    mock_embedding_model: MagicMock,
) -> None:
    """Test successful search."""
    # Mock the session to return a list of nodes
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = [
        {
            "n": {
                "id": "1",
                "name": "Test Node",
                "properties": {"id": "1", "name": "Test Node"},
            },
            "labels": ["Node"],
        }
    ]
    # Configure the mock session for the search query
    mock_neo4j_session.run.return_value = mock_result

    response = client.post(
        "/mcp/search",
        json={"query": "test", "limit": 10},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "results": [
            {
                "node_id": "1",
                "score": 0.0,  # Mock score
                "labels": ["Node"],
                "properties": {"id": "1", "name": "Test Node"},
            }
        ]
    }


@pytest.mark.asyncio
async def test_initialize_success(client: TestClient) -> None:
    """Test successful initialization."""
    response = client.post("/mcp/initialize")
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "protocol_version" in data
    assert "capabilities" in data
    assert "instructions" in data


@pytest.mark.asyncio
async def test_list_resources(client: TestClient) -> None:
    """Test listing resources."""
    response = client.get("/mcp/resources/list")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == ["nodes", "relationships", "search"]


@pytest.mark.asyncio
async def test_get_resource_invalid(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test getting an invalid resource."""
    response = client.get("/mcp/resources/get/invalid")
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid resource type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_tool_dispatch_missing_name(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test tool dispatch with missing tool name."""
    response = client.post("/mcp/rpc/tools/dispatch", json={})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Missing tool name"}


@pytest.mark.asyncio
async def test_tool_dispatch_unknown_tool(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test tool dispatch with unknown tool."""
    response = client.post(
        "/mcp/rpc/tools/dispatch",
        json={"tool_name": "unknown", "parameters": {}},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Unknown tool: unknown"}


@pytest.mark.asyncio
async def test_mcp_tool_dispatch_success(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test successful tool dispatch."""
    mock_result = {"p": {"id": "1", "name": "Test Person"}}
    mock_neo4j_session.run.return_value.all.return_value = [mock_result]

    response = client.post(
        "/mcp/rpc/tools/dispatch",
        json={
            "tool_name": "match_role",
            "parameters": {
                "required_skills": ["Python"],
                "years_experience": {"Python": 5},
            },
        },
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "match_score" in data
    assert "skill_gaps" in data
    assert "matching_skills" in data


@pytest.mark.asyncio
async def test_mcp_tool_dispatch_invalid_params(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test tool dispatch with invalid parameters."""
    response = client.post(
        "/mcp/rpc/tools/dispatch",
        json={
            "tool_name": "match_role",
            "parameters": {
                "years_experience": "invalid",  # Should be a dict
            },
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    error_msg = response.json()["detail"]
    assert "years_experience" in error_msg
    assert "dictionary" in error_msg


@pytest.mark.asyncio
async def test_mcp_jsonrpc_initialize(client: TestClient) -> None:
    """Test JSON-RPC initialize method."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.initialize",
        params={},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert data["id"] == 1
    result = data["result"]
    assert "protocol_version" in result
    assert "capabilities" in result
    assert "instructions" in result


@pytest.mark.asyncio
async def test_mcp_jsonrpc_search_success(
    client: TestClient,
    mock_neo4j_session: AsyncSession,
    mock_embedding_model: MagicMock,
) -> None:
    """Test successful JSON-RPC search."""
    # Mock the session to return a list of nodes
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = [
        {
            "n": {"id": "1", "name": "Test Node"},
            "labels": ["Node"],
        }
    ]
    mock_neo4j_session.run.return_value = mock_result

    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.search",
        params={"query": "test", "limit": 10},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert data["id"] == 1
    assert data["result"] == [
        {
            "node_id": "1",
            "score": 0.0,  # Mock score
            "labels": ["Node"],
            "properties": {"id": "1", "name": "Test Node"},
        }
    ]


@pytest.mark.asyncio
async def test_mcp_jsonrpc_search_missing_query(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test JSON-RPC search with missing query."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.search",
        params={},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["id"] == 1
    assert data["error"]["code"] == ERROR_INVALID_PARAMS
    assert "Missing query parameter" in data["error"]["message"]


@pytest.mark.asyncio
async def test_mcp_jsonrpc_tool_success(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test successful JSON-RPC tool dispatch."""
    mock_result = {"p": {"id": "1", "name": "Test Person"}}
    mock_neo4j_session.run.return_value.all.return_value = [mock_result]

    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.tool",
        params={
            "name": "match_role",
            "parameters": {
                "required_skills": ["Python"],
                "years_experience": {"Python": 5},
            },
        },
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert data["id"] == 1
    result = data["result"]
    assert "match_score" in result
    assert "skill_gaps" in result
    assert "matching_skills" in result


@pytest.mark.asyncio
async def test_mcp_jsonrpc_tool_missing_name(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test JSON-RPC tool dispatch with missing tool name."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.tool",
        params={},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["id"] == 1
    assert data["error"]["code"] == ERROR_INVALID_PARAMS
    assert "Missing tool name" in data["error"]["message"]


@pytest.mark.asyncio
async def test_mcp_jsonrpc_tool_unknown(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test JSON-RPC tool dispatch with unknown tool."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.tool",
        params={"name": "unknown", "parameters": {}},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["id"] == 1
    assert data["error"]["code"] == ERROR_INVALID_PARAMS
    assert "Unknown tool" in data["error"]["message"]


@pytest.mark.asyncio
async def test_mcp_jsonrpc_invalid_method(
    client: TestClient, mock_neo4j_session: AsyncSession
) -> None:
    """Test JSON-RPC with invalid method."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="invalid.method",
        params={},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["id"] == 1
    assert data["error"]["code"] == ERROR_METHOD_NOT_FOUND
    assert "Method not found" in data["error"]["message"]
