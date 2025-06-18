"""Tests for the MCP server."""

from http import HTTPStatus
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from fastapi import HTTPException
from fastapi.testclient import TestClient

from skill_sphere_mcp.api.jsonrpc import ERROR_INVALID_PARAMS
from skill_sphere_mcp.api.jsonrpc import ERROR_METHOD_NOT_FOUND
from skill_sphere_mcp.api.jsonrpc import JSONRPCRequest
from skill_sphere_mcp.api.mcp.routes import get_db_session
from skill_sphere_mcp.app import create_app

from .constants import HTTP_OK
from .constants import HTTP_UNPROCESSABLE_ENTITY


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.run = AsyncMock()

    def run_side_effect(*args, **kwargs):
        query = args[0] if args else ""
        params = args[1] if len(args) > 1 else kwargs
        # Normalize query string to ignore whitespace/newlines
        norm_query = " ".join(query.split())

        # For handle_get_entity (MATCH (n) WHERE n.id = $entity_id OR n.name = $entity_id RETURN n LIMIT 1)
        if "MATCH (n) WHERE n.id = $entity_id OR n.name = $entity_id RETURN n LIMIT 1" in norm_query:
            # Simulate not found for 'nonexistent'
            if params and (params.get("entity_id") == "nonexistent"):
                mock_result = AsyncMock()
                mock_result.single = AsyncMock(return_value=None)
                return mock_result
            # Otherwise, return a dummy entity
            mock_result = AsyncMock()
            mock_result.single = AsyncMock(
                return_value={
                    "n": {"id": "someid", "name": "Some Entity", "type": "Skill"}
                }
            )
            return mock_result

        # For get_entity_by_id (MATCH (n) WHERE n.id = $entity_id ...)
        elif (
            "MATCH (n) WHERE n.id = $entity_id RETURN n, [(n)-[r]->(m) | {type: type(r), target: m.id}] as relationships"
            in norm_query
        ):
            # Simulate not found for 'nonexistent'
            if params and (params.get("entity_id") == "nonexistent"):
                mock_result = AsyncMock()
                mock_result.single = AsyncMock(return_value=None)
                return mock_result
            # Otherwise, return a dummy entity with relationships
            mock_result = AsyncMock()
            mock_result.single = AsyncMock(
                return_value={
                    "n": {"id": "someid", "name": "Some Entity", "type": "Skill"},
                    "relationships": [
                        {
                            "type": "RELATES_TO",
                            "target": "otherid"
                        }
                    ]
                }
            )
            return mock_result

        # For match_role (MATCH (p:Person))
        elif "MATCH (p:Person)" in norm_query:
            mock_result = AsyncMock()
            mock_result.all = AsyncMock(
                return_value=[
                    {
                        "p": {
                            "id": "1",
                            "name": "Test Person",
                            "skills": ["Python", "FastAPI"],
                            "experience": {"Python": 5, "FastAPI": 3},
                        }
                    }
                ]
            )
            return mock_result

        # For explain_match (MATCH (s:Skill))
        elif "MATCH (s:Skill" in norm_query:
            mock_result = AsyncMock()
            mock_result.single = AsyncMock(
                return_value={
                    "s": {"id": "1", "name": "Python"},
                    "projects": [
                        {
                            "id": "p1",
                            "name": "Project A",
                            "description": "Python project",
                        }
                    ],
                    "certifications": [
                        {
                            "id": "c1",
                            "name": "Python Cert",
                            "description": "Python certification",
                        }
                    ],
                }
            )
            return mock_result

        # For graph_search (MATCH (n))
        elif "MATCH (n)" in norm_query:
            mock_result = AsyncMock()
            mock_result.all = AsyncMock(
                return_value=[
                    {
                        "n": {
                            "id": "1",
                            "name": "Python",
                            "type": "Skill",
                            "description": "Python programming language",
                            "labels": ["Skill"],
                            "properties": {
                                "name": "Python",
                                "description": "Python programming language",
                            },
                        }
                    },
                    {
                        "n": {
                            "id": "2",
                            "name": "FastAPI",
                            "type": "Skill",
                            "description": "FastAPI web framework",
                            "labels": ["Skill"],
                            "properties": {
                                "name": "FastAPI",
                                "description": "FastAPI web framework",
                            },
                        }
                    },
                ]
            )
            return mock_result

        # Default case
        mock_result = AsyncMock()
        mock_result.all = AsyncMock(return_value=[])
        return mock_result

    session.run.side_effect = run_side_effect
    return session


@pytest.fixture
def client(mock_db_session):
    """Create a test client with mocked dependencies."""
    app = create_app()
    app.dependency_overrides[get_db_session] = lambda: mock_db_session
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_health_check(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_entity_not_found(client: TestClient) -> None:
    """Test getting a non-existent entity."""
    response = client.get("/mcp/entities/nonexistent")
    assert response.status_code == 404
    assert "Entity not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_entity_invalid_id(client: TestClient) -> None:
    """Test getting an entity with invalid ID."""
    response = client.get("/mcp/entities/!@#")
    assert response.status_code == 422
    assert "Invalid entity ID" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_entity_success(client: TestClient) -> None:
    """Test getting an entity successfully."""
    response = client.get("/mcp/entities/someid")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "someid"
    assert data["name"] == "Some Entity"
    assert data["type"] == "Skill"


@pytest.mark.asyncio
async def test_get_entity_database_error(client: TestClient, mock_db_session) -> None:
    """Test handling database errors when getting an entity."""
    # Mock a database error
    mock_db_session.run.side_effect = Exception("Database connection error")

    response = client.get("/mcp/entities/someid")
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "Database error" in response.json()["detail"]


@pytest.mark.asyncio
async def test_search_success(client: TestClient) -> None:
    """Test successful search."""
    response = client.post(
        "/mcp/search",
        json={"query": "Python", "limit": 10},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0
    assert "node" in data["results"][0]
    assert "name" in data["results"][0]["node"]


@pytest.mark.asyncio
async def test_list_resources(client: TestClient) -> None:
    """Test listing resources."""
    response = client.get("/mcp/resources/list")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == ["nodes", "relationships", "search"]


@pytest.mark.asyncio
async def test_get_resource_invalid(client: TestClient) -> None:
    """Test getting an invalid resource."""
    response = client.get("/mcp/resources/get/invalid")
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Invalid resource type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_tool_dispatch_missing_name(client: TestClient) -> None:
    """Test tool dispatch with missing tool name."""
    response = client.post("/mcp/rpc/tools/dispatch", json={})
    assert response.status_code == 422
    assert response.json()["detail"] == "Tool name is required"


@pytest.mark.asyncio
async def test_tool_dispatch_unknown_tool(client: TestClient) -> None:
    """Test tool dispatch with unknown tool."""
    response = client.post(
        "/mcp/rpc/tools/dispatch",
        json={"tool_name": "unknown", "parameters": {}},
    )
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY
    assert response.json() == {"detail": "Unknown tool: unknown"}


@pytest.mark.asyncio
async def test_mcp_tool_dispatch_success(client: TestClient) -> None:
    """Test successful tool dispatch."""
    response = client.post(
        "/mcp/rpc/tools/dispatch",
        json={
            "tool_name": "skill.match_role",
            "parameters": {
                "required_skills": ["Python"],
                "years_experience": {"Python": 5},
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "data" in data


@pytest.mark.asyncio
async def test_mcp_tool_dispatch_invalid_params(client: TestClient) -> None:
    """Test MCP tool dispatch with invalid parameters."""
    response = client.post(
        "/mcp/rpc/tools/dispatch",
        json={
            "tool_name": "skill.match_role",
            "parameters": {},
        },
    )
    assert response.status_code == 422
    assert "Required skills are missing" in response.json()["detail"]


@pytest.mark.asyncio
async def test_mcp_jsonrpc_search_success(client: TestClient) -> None:
    """Test successful JSON-RPC search."""
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "mcp.search",
        "params": {"query": "Python", "limit": 10},
    }
    response = client.post("/mcp/rpc", json=request)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "result" in data
    assert isinstance(data["result"], dict)
    assert "results" in data["result"]
    assert isinstance(data["result"]["results"], list)


@pytest.mark.asyncio
async def test_mcp_jsonrpc_search_missing_query(client: TestClient) -> None:
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
    assert data["error"] == {"code": ERROR_INVALID_PARAMS["code"], "message": "Query is required"}


@pytest.mark.asyncio
async def test_mcp_jsonrpc_tool_success(client: TestClient) -> None:
    """Test successful JSON-RPC tool dispatch."""
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
    assert "match_score" in data["result"]
    assert "skill_gaps" in data["result"]
    assert "matching_skills" in data["result"]


@pytest.mark.asyncio
async def test_mcp_jsonrpc_tool_missing_name(client: TestClient) -> None:
    """Test JSON-RPC tool dispatch with missing tool name."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.tool",
        params={},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["id"] == 1
    assert data["error"]["message"] == "Tool name is required"


@pytest.mark.asyncio
async def test_mcp_jsonrpc_tool_unknown(client: TestClient) -> None:
    """Test JSON-RPC tool dispatch with unknown tool."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="mcp.tool",
        params={
            "name": "unknown_tool",
            "parameters": {},
        },
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["error"]["code"] == ERROR_INVALID_PARAMS["code"]
    assert "Unknown tool" in data["error"]["message"]
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_mcp_jsonrpc_invalid_method(client: TestClient) -> None:
    """Test JSON-RPC with invalid method."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="invalid.method",
        params={},
        id=1,
    )
    response = client.post("/mcp/rpc", json=request.__dict__)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "error" in data
    assert data["id"] == 1
    assert data["error"]["message"] == "Method not found"


@pytest.mark.asyncio
async def test_match_role_endpoint(client: TestClient) -> None:
    """Test match role endpoint."""
    response = client.post(
        "/match_role",
        json={
            "required_skills": ["Python", "FastAPI"],
            "years_experience": {"Python": 5, "FastAPI": 3},
        },
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "match_score" in data
    assert "skill_gaps" in data
    assert "matching_skills" in data


@pytest.mark.asyncio
async def test_explain_match_endpoint(client: TestClient) -> None:
    """Test explain match endpoint."""
    response = client.post(
        "/explain_match",
        json={
            "skill_id": "1",
            "role_requirement": "Python developer with FastAPI experience",
        },
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "explanation" in data
    assert "evidence" in data


@pytest.mark.asyncio
async def test_graph_search_endpoint(client: TestClient) -> None:
    """Test graph search endpoint."""
    response = client.post(
        "/graph_search",
        json={"query": "Python developer with FastAPI experience"},
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_match_role_invalid_input(client: TestClient) -> None:
    """Test match role endpoint with invalid input."""
    response = client.post(
        "/match_role",
        json={
            "role": "Software Engineer",
            "skills": [],  # Empty skills list
            "experience": {},
        },
    )
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_explain_match_invalid_input(client: TestClient) -> None:
    """Test explain match endpoint with invalid input."""
    response = client.post(
        "/explain_match",
        json={
            "role": "Software Engineer",
            "skills": [],  # Empty skills list
            "experience": {},
        },
    )
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_graph_search_invalid_input(client: TestClient) -> None:
    """Test graph search endpoint with invalid input."""
    response = client.post(
        "/graph_search",
        json={"query": ""},  # Empty query
    )
    assert response.status_code == HTTP_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
