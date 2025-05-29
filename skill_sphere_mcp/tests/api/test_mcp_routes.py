# pylint: disable=redefined-outer-name
"""Tests for MCP routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio
from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.api import mcp_routes
from skill_sphere_mcp.api.jsonrpc import (
    ERROR_INTERNAL,
    ERROR_INVALID_PARAMS,
    ERROR_METHOD_NOT_FOUND,
    JSONRPCHandler,
    JSONRPCRequest,
    JSONRPCResponse,
)
from skill_sphere_mcp.api.mcp_routes import (
    SKILL_MATCH_THRESHOLD,
    InitializeResponse,
    ToolRequest,
    get_resource,
    initialize,
    list_resources,
    rpc_match_role_handler,
)
from skill_sphere_mcp.api.models import InitializeRequest
from skill_sphere_mcp.cv.generator import generate_cv
from skill_sphere_mcp.tools.dispatcher import dispatch_tool

# Create a test instance of JSONRPCHandler
test_rpc_handler = JSONRPCHandler()

# Test data
MOCK_SKILL_ID = "123"
MOCK_RESOURCE_TYPE = "skills.node"
MOCK_TOOL_NAME = "skill.match_role"
MOCK_SKILLS = ["Python", "FastAPI"]
MOCK_YEARS = {"Python": 5, "FastAPI": 3}
MOCK_MATCH_RESULT = {
    "match_score": 0.85,
    "matching_skills": [{"name": "Python"}],
    "skill_gaps": [],
}

# HTTP status codes
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501


@pytest_asyncio.fixture
async def mock_session():
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def test_initialize() -> None:
    """Test MCP initialization endpoint."""
    response = await initialize()
    assert isinstance(response, InitializeResponse)
    assert response.protocol_version == "1.0"
    assert (
        "semantic_search" in response.capabilities
        or "resources" in response.capabilities
    )
    assert isinstance(response.instructions, str)


@pytest_asyncio.fixture
async def test_list_resources() -> None:
    """Test resource listing endpoint."""
    resources = await list_resources()
    assert isinstance(resources, list)
    assert len(resources) > 0
    assert all(isinstance(r, str) for r in resources)


@pytest_asyncio.fixture
async def test_get_resource_success() -> None:
    """Test successful resource retrieval."""
    response = await get_resource(MOCK_RESOURCE_TYPE)
    assert isinstance(response, dict)
    assert "type" in response
    assert "schema" in response


@pytest_asyncio.fixture
async def test_get_resource_not_found() -> None:
    """Test resource retrieval with non-existent resource."""
    # The endpoint now returns schema for any valid resource type, so this test is not applicable.
    # We'll skip this test.
    pytest.skip("Resource not found test is not applicable for schema-only endpoint.")


@pytest_asyncio.fixture
async def test_get_resource_invalid_type() -> None:
    """Test resource retrieval with invalid resource type."""
    with pytest.raises(HTTPException) as exc_info:
        await get_resource("invalid.type")
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest_asyncio.fixture
async def test_get_resource_invalid_id_format() -> None:
    """Test resource retrieval with invalid ID format."""
    with pytest.raises(HTTPException) as exc_info:
        await get_resource("not_a_number")
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest_asyncio.fixture
async def test_get_resource_database_error() -> None:
    """Test resource retrieval with database error."""
    # The endpoint now returns schema for any valid resource type, so this test is not applicable.
    pytest.skip("Database error test is not applicable for schema-only endpoint.")


@pytest_asyncio.fixture
async def test_dispatch_tool_success(mock_session: AsyncMock) -> None:
    """Test successful tool dispatch."""
    parameters = {
        "required_skills": ["Python", "FastAPI"],
        "years_experience": {"Python": 5},
    }
    request = ToolRequest(tool_name="skill.match_role", parameters=parameters)
    # Patch the DB result to return skills compatible with match_role
    mock_record = {"p": {"name": "John Doe", "skills": ["Python", "FastAPI"]}}
    mock_session.run.return_value.all.return_value = [mock_record]
    response = await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert isinstance(response, dict)
    assert "match_score" in response
    assert "skill_gaps" in response
    assert "matching_skills" in response
    assert response["match_score"] == pytest.approx(1.0)
    assert "Python" in [skill["name"] for skill in response["matching_skills"]]


@pytest_asyncio.fixture
async def test_dispatch_tool_invalid_name(mock_session: AsyncMock) -> None:
    """Test tool dispatch with invalid tool name."""
    request = ToolRequest(tool_name="invalid.tool", parameters={})
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_NOT_FOUND


@pytest_asyncio.fixture
async def test_dispatch_tool_invalid_params(mock_session: AsyncMock) -> None:
    """Test tool dispatch with invalid parameters."""
    request = ToolRequest(tool_name=MOCK_TOOL_NAME, parameters={})
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest_asyncio.fixture
async def test_explain_match_tool(mock_session: AsyncMock) -> None:
    """Test explain match tool handler."""
    parameters = {
        "skill_id": "123",
        "role_requirement": "Python developer with 5 years experience",
    }
    request = ToolRequest(tool_name="skill.explain_match", parameters=parameters)
    response = await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert isinstance(response, dict)
    assert "explanation" in response
    assert "evidence" in response


@pytest_asyncio.fixture
async def test_generate_cv_tool(mock_session: AsyncMock) -> None:
    """Test CV generation tool handler."""
    parameters = {
        "target_keywords": ["Python", "FastAPI"],
        "format": "markdown",
    }
    request = ToolRequest(tool_name="cv.generate", parameters=parameters)
    mock_record = {
        "p": {"name": "John Doe"},
        "skills": [{"name": "Python"}, {"name": "FastAPI"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record
    response = await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert isinstance(response, dict)
    assert "content" in response
    assert "format" in response


@pytest_asyncio.fixture
async def test_graph_search_tool(mock_session: AsyncMock) -> None:
    """Test graph search tool handler."""
    parameters = {
        "query": "Python developer",
        "top_k": 5,
    }
    request = ToolRequest(tool_name="graph.search", parameters=parameters)
    response = await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert isinstance(response, dict)
    assert "results" in response
    assert isinstance(response["results"], list)


@pytest_asyncio.fixture
async def test_tool_handler_error(mock_session: AsyncMock) -> None:
    """Test error handling in tool handlers."""
    parameters = {"required_skills": ["Python"]}
    request = ToolRequest(tool_name=MOCK_TOOL_NAME, parameters=parameters)
    # Simulate error by passing invalid tool name
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool("invalid.tool", request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_NOT_FOUND


@pytest_asyncio.fixture
async def test_initialize_invalid_version() -> None:
    """Test MCP initialization with invalid version."""
    response = await initialize()
    assert response.protocol_version == "1.0"  # Should return supported version


@pytest.mark.asyncio
async def test_get_resource_skills_relation() -> None:
    """Test resource retrieval for skills relation type."""
    response = await get_resource("skills.relation")
    assert isinstance(response, dict)
    assert "type" in response
    assert "schema" in response


@pytest.mark.asyncio
async def test_get_resource_profiles_detail() -> None:
    """Test resource retrieval for profiles detail type."""
    response = await get_resource("profiles.detail")
    assert isinstance(response, dict)
    assert "type" in response
    assert "schema" in response


@pytest.mark.asyncio
async def test_explain_match_tool_invalid_params(mock_session: AsyncMock) -> None:
    """Test explain match tool with invalid parameters."""
    parameters = {
        "skill_id": "123",
        # Missing required role_requirement
    }
    request = ToolRequest(tool_name="skill.explain_match", parameters=parameters)
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_cv_tool_invalid_format(mock_session: AsyncMock) -> None:
    """Test CV generation tool with invalid format."""
    parameters = {
        "target_keywords": ["Python"],
        "format": "invalid_format",  # Invalid format
    }
    request = ToolRequest(tool_name="cv.generate", parameters=parameters)
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_graph_search_tool_invalid_top_k(mock_session: AsyncMock) -> None:
    """Test graph search tool with invalid top_k value."""
    parameters = {
        "query": "Python developer",
        "top_k": 0,  # Invalid top_k value
    }
    request = ToolRequest(tool_name="graph.search", parameters=parameters)
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_match_role_tool_empty_skills(mock_session: AsyncMock) -> None:
    """Test match role tool with empty skills list."""
    parameters: dict = {
        "required_skills": [],  # Empty skills list
        "years_experience": {},
    }
    request = ToolRequest(tool_name=MOCK_TOOL_NAME, parameters=parameters)
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_match_role_tool_invalid_experience(mock_session: AsyncMock) -> None:
    """Test match role tool with invalid experience format."""
    parameters = {
        "required_skills": ["Python"],
        "years_experience": {"Python": "invalid"},  # Invalid experience value
    }
    request = ToolRequest(tool_name=MOCK_TOOL_NAME, parameters=parameters)
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request.tool_name, request.parameters, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_match_role_success() -> None:
    """Test match_role returns expected result."""
    params = {"required_skills": ["Python"], "years_experience": {}}
    mock_session = AsyncMock()
    # Simulate DB returning a skill node with experience_years
    mock_skill = {"s": {"name": "Python"}, "relationships": [], "experience_years": [5]}
    mock_session.run.return_value.__aiter__.return_value = [mock_skill]
    result = await mcp_routes.match_role(params, mock_session)
    assert "match_score" in result
    assert result["match_score"] == pytest.approx(1.0)
    assert result["skill_gaps"] == []
    assert result["matching_skills"][0]["name"] == "Python"


@pytest.mark.asyncio
async def test_match_role_invalid_params() -> None:
    """Test match_role with invalid parameters raises HTTPException."""
    mock_session = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await mcp_routes.match_role({}, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_explain_match_success() -> None:
    """Test explain_match returns expected result."""
    params = {"skill_id": "1", "role_requirement": "Python dev"}
    mock_session = AsyncMock()
    # Simulate DB returning a skill node with evidence
    mock_record = {
        "s": {"name": "Python"},
        "evidence": [
            {"rel": MagicMock(type="HAS_SKILL"), "target": {"name": "FastAPI"}}
        ],
    }
    mock_session.run.return_value.single.return_value = mock_record
    result = await mcp_routes.explain_match(params, mock_session)
    assert "explanation" in result
    assert "evidence" in result
    assert result["evidence"][0]["type"] == "HAS_SKILL"


@pytest.mark.asyncio
async def test_explain_match_invalid_params() -> None:
    """Test explain_match with invalid parameters raises HTTPException."""
    mock_session = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await mcp_routes.explain_match({}, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_explain_match_value_error() -> None:
    """Test explain_match with invalid skill_id format raises HTTPException."""
    params = {"skill_id": "not_a_number", "role_requirement": "Python dev"}
    mock_session = AsyncMock()
    mock_session.run.side_effect = ValueError()
    with pytest.raises(HTTPException) as exc_info:
        await mcp_routes.explain_match(params, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_cv_success() -> None:
    """Test generate_cv returns markdown CV."""
    params = {"target_keywords": ["Python"], "format": "markdown"}
    mock_session = AsyncMock()
    mock_record = {
        "p": {"name": "John"},
        "skills": [{"name": "Python"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record
    result = await generate_cv(params, mock_session)
    assert result["format"] == "markdown"
    assert "# John" in result["content"]
    assert "- Python" in result["content"]


@pytest.mark.asyncio
async def test_generate_cv_invalid_params() -> None:
    """Test generate_cv with invalid parameters raises HTTPException."""
    mock_session = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv({}, mock_session)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_cv_profile_not_found() -> None:
    """Test generate_cv when profile not found raises HTTPException."""
    params = {"target_keywords": ["Python"], "format": "markdown"}
    mock_session = AsyncMock()
    mock_session.run.return_value.single.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(params, mock_session)
    assert exc_info.value.status_code == HTTP_NOT_FOUND


@pytest.mark.asyncio
async def test_generate_cv_format_not_implemented() -> None:
    """Test generate_cv with unsupported format raises HTTPException."""
    params = {"target_keywords": ["Python"], "format": "pdf"}
    mock_session = AsyncMock()
    mock_record = {
        "p": {"name": "John"},
        "skills": [],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(params, mock_session)
    assert exc_info.value.status_code == HTTP_NOT_IMPLEMENTED


@pytest.mark.asyncio
async def test_graph_search_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test graph_search returns results."""
    params = {"query": "Python", "top_k": 1}
    mock_session = AsyncMock()
    # Patch embeddings.search to return a fake result
    monkeypatch.setattr(
        mcp_routes.embeddings,
        "search",
        AsyncMock(
            return_value=[
                {
                    "node_id": "1",
                    "score": 0.9,
                    "labels": ["Skill"],
                    "properties": {"name": "Python"},
                }
            ]
        ),
    )

    # Patch MODEL.encode to return a numpy array
    class DummyModel:
        """Mock model class for testing graph search functionality."""

        def encode(self, _query: str) -> object:
            """Mock encode method that returns a dummy tensor."""

            class DummyTensor:
                """Mock tensor class that returns a numpy array of ones."""

                def numpy(self) -> np.ndarray:
                    """Return a numpy array of ones with shape (128,)."""
                    return np.ones(128)

            return DummyTensor()

    monkeypatch.setattr(mcp_routes, "MODEL", DummyModel())
    result = await mcp_routes.graph_search(params, mock_session)
    assert "results" in result
    assert result["results"][0]["node_id"] == "1"


@pytest.mark.asyncio
async def test_graph_search_importerror(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test graph_search falls back to random embedding if MODEL is None."""
    params = {"query": "Python", "top_k": 1}
    mock_session = AsyncMock()
    monkeypatch.setattr(
        mcp_routes.embeddings,
        "search",
        AsyncMock(
            return_value=[
                {
                    "node_id": "1",
                    "score": 0.9,
                    "labels": ["Skill"],
                    "properties": {"name": "Python"},
                }
            ]
        ),
    )
    monkeypatch.setattr(mcp_routes, "MODEL", None)
    result = await mcp_routes.graph_search(params, mock_session)
    assert "results" in result
    assert result["results"][0]["node_id"] == "1"


@pytest.mark.asyncio
async def test_handle_skill_match_success() -> None:
    """Test successful skill matching."""
    mock_session = AsyncMock()
    # Simulate DB returning a skill node with experience_years
    mock_skill = {"s": {"name": "Python"}, "relationships": [], "experience_years": [5]}
    mock_session.run.return_value.__aiter__.return_value = [mock_skill]
    with patch(
        "skill_sphere_mcp.api.mcp_routes._calculate_semantic_score", return_value=1.0
    ):
        params = {
            "required_skills": ["Python"],
            "years_experience": {"Python": 5},
        }
        result = await rpc_match_role_handler(params, mock_session)
        assert "match_score" in result
        assert result["match_score"] == pytest.approx(1.0)
        assert len(result["matching_skills"]) == 1
        assert len(result["skill_gaps"]) == 0


@pytest.mark.asyncio
async def test_handle_skill_match_below_threshold() -> None:
    """Test skill matching below threshold."""
    mock_session = AsyncMock()
    with patch("skill_sphere_mcp.api.mcp_routes.dispatch_tool") as mock_dispatch:
        mock_dispatch.return_value = {
            "match_score": SKILL_MATCH_THRESHOLD - 0.1,
            "matching_skills": [],
            "skill_gaps": MOCK_SKILLS,
        }
        params = {
            "required_skills": MOCK_SKILLS,
            "years_experience": MOCK_YEARS,
        }
        result = await rpc_match_role_handler(params, mock_session)
        assert "match_score" in result
        assert result["match_score"] < SKILL_MATCH_THRESHOLD
        assert len(result["matching_skills"]) == 0
        assert len(result["skill_gaps"]) == len(MOCK_SKILLS)


@pytest.mark.asyncio
async def test_handle_skill_match_error() -> None:
    """Test skill matching with error."""
    with patch("skill_sphere_mcp.api.mcp_routes.dispatch_tool") as mock_dispatch:
        mock_dispatch.side_effect = Exception("Matching error")

        request = JSONRPCRequest(
            jsonrpc="2.0",
            method="skill.match_role",
            params={
                "required_skills": MOCK_SKILLS,
                "years_experience": MOCK_YEARS,
            },
            id=1,
        )
        result = await test_rpc_handler.handle_request(request)

        assert isinstance(result, JSONRPCResponse)
        assert result.jsonrpc == "2.0"
        assert result.id == 1
        assert result.error is not None
        assert result.error(ERROR_INTERNAL, "Internal error", None) is not None


@pytest.mark.asyncio
async def test_handle_jsonrpc_request_success() -> None:
    """Test successful JSON-RPC request handling."""
    mock_session = AsyncMock()
    # Simulate DB returning a skill node with experience_years
    mock_skill = {"s": {"name": "Python"}, "relationships": [], "experience_years": [5]}
    mock_session.run.return_value.__aiter__.return_value = [mock_skill]
    with patch(
        "skill_sphere_mcp.api.mcp_routes._calculate_semantic_score", return_value=1.0
    ):
        params = {
            "required_skills": ["Python"],
            "years_experience": {"Python": 5},
        }
        result = await rpc_match_role_handler(params, mock_session)
        assert "match_score" in result
        assert result["match_score"] == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_handle_jsonrpc_request_invalid_method() -> None:
    """Test JSON-RPC request with invalid method."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="invalid.method",
        params={},
        id=1,
    )
    result = await test_rpc_handler.handle_request(request)

    assert isinstance(result, JSONRPCResponse)
    assert result.jsonrpc == "2.0"
    assert result.id == 1
    assert result.error is not None
    assert result.error(ERROR_METHOD_NOT_FOUND, "Method not found", None) is not None


@pytest.mark.asyncio
async def test_handle_jsonrpc_request_invalid_params() -> None:
    """Test JSON-RPC request with invalid parameters."""
    request = JSONRPCRequest(
        jsonrpc="2.0",
        method="skill.match_role",
        params={},
        id=1,
    )
    result = await test_rpc_handler.handle_request(request)

    assert isinstance(result, JSONRPCResponse)
    assert result.jsonrpc == "2.0"
    assert result.id == 1
    assert result.error is not None
    assert result.error(ERROR_INVALID_PARAMS, "Invalid params", None) is not None


@pytest.mark.asyncio
async def test_handle_jsonrpc_request_internal_error() -> None:
    """Test JSON-RPC request with internal error."""
    with patch("skill_sphere_mcp.api.mcp_routes.dispatch_tool") as mock_dispatch:
        mock_dispatch.side_effect = Exception("Internal error")

        request = JSONRPCRequest(
            jsonrpc="2.0",
            method="skill.match_role",
            params={
                "required_skills": MOCK_SKILLS,
                "years_experience": MOCK_YEARS,
            },
            id=1,
        )
        result = await test_rpc_handler.handle_request(request)

        assert isinstance(result, JSONRPCResponse)
        assert result.jsonrpc == "2.0"
        assert result.id == 1
        assert result.error is not None
        assert result.error(ERROR_INTERNAL, "Internal error", None) is not None
