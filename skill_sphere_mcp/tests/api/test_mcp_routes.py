"""Tests for MCP routes."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.api.mcp_routes import (
    InitializeRequest,
    InitializeResponse,
    ResourceRequest,
    ToolRequest,
    dispatch_tool,
    get_resource,
    initialize,
    list_resources,
)

# Test data
MOCK_TOKEN = "test_token"
MOCK_SKILL_ID = "123"
MOCK_RESOURCE_TYPE = "skills.node"
MOCK_TOOL_NAME = "skill.match_role"

# HTTP status codes
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_token() -> str:
    """Create a mock PAT token."""
    return MOCK_TOKEN


@pytest.mark.asyncio
async def test_initialize(token: str) -> None:
    """Test MCP initialization endpoint."""
    request = InitializeRequest(protocol_version="1.0")
    response = await initialize(request, token)

    assert isinstance(response, InitializeResponse)
    assert response.protocol_version == "1.0"
    assert "resources" in response.capabilities
    assert "tools" in response.capabilities
    assert isinstance(response.instructions, str)


@pytest.mark.asyncio
async def test_list_resources(token: str) -> None:
    """Test resource listing endpoint."""
    resources = await list_resources(token)
    assert isinstance(resources, list)
    assert len(resources) > 0
    assert all(isinstance(r, str) for r in resources)


@pytest.mark.asyncio
async def test_get_resource_success(session: AsyncMock, token: str) -> None:
    """Test successful resource retrieval."""
    mock_record = {
        "n": MagicMock(id=123, labels=["Skill"], properties={"name": "Python"}),
        "labels": ["Skill"],
        "props": {"name": "Python"},
    }
    session.run.return_value.single.return_value = mock_record

    request = ResourceRequest(
        resource_type=MOCK_RESOURCE_TYPE, resource_id=MOCK_SKILL_ID
    )
    response = await get_resource(request, session, token)

    assert isinstance(response, dict)
    assert "n" in response
    assert "labels" in response
    assert "props" in response


@pytest.mark.asyncio
async def test_get_resource_not_found(session: AsyncMock, token: str) -> None:
    """Test resource retrieval with non-existent resource."""
    session.run.return_value.single.return_value = None

    request = ResourceRequest(
        resource_type=MOCK_RESOURCE_TYPE, resource_id=MOCK_SKILL_ID
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_resource(request, session, token)
    assert exc_info.value.status_code == HTTP_NOT_FOUND


@pytest.mark.asyncio
async def test_get_resource_invalid_type(session: AsyncMock, token: str) -> None:
    """Test resource retrieval with invalid resource type."""
    request = ResourceRequest(resource_type="invalid.type", resource_id=MOCK_SKILL_ID)
    with pytest.raises(HTTPException) as exc_info:
        await get_resource(request, session, token)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_dispatch_tool_success(session: AsyncMock, token: str) -> None:
    """Test successful tool dispatch."""
    parameters = {
        "required_skills": ["Python", "FastAPI"],
        "years_experience": {"Python": 5},
    }
    request = ToolRequest(tool_name=MOCK_TOOL_NAME, parameters=parameters)

    with patch("skill_sphere_mcp.api.mcp_routes.match_role") as mock_match_role:
        mock_match_role.return_value = {
            "match_score": 0.8,
            "skill_gaps": [],
            "matching_skills": [],
        }
        response = await dispatch_tool(request, session, token)

    assert isinstance(response, dict)
    assert "match_score" in response
    assert "skill_gaps" in response
    assert "matching_skills" in response


@pytest.mark.asyncio
async def test_dispatch_tool_invalid_name(session: AsyncMock, token: str) -> None:
    """Test tool dispatch with invalid tool name."""
    request = ToolRequest(tool_name="invalid.tool", parameters={})
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request, session, token)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST


@pytest.mark.asyncio
async def test_dispatch_tool_invalid_params(session: AsyncMock, token: str) -> None:
    """Test tool dispatch with invalid parameters."""
    request = ToolRequest(tool_name=MOCK_TOOL_NAME, parameters={})
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool(request, session, token)
    assert exc_info.value.status_code == HTTP_BAD_REQUEST
