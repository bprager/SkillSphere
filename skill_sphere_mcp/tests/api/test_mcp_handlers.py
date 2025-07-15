"""Tests for MCP handlers."""

from typing import Any
from typing import List
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.api.mcp.handlers import get_resource
from skill_sphere_mcp.api.mcp.handlers import handle_get_entity
from skill_sphere_mcp.api.mcp.handlers import handle_list_resources
from skill_sphere_mcp.api.mcp.handlers import handle_search
from skill_sphere_mcp.api.mcp.handlers import handle_tool_dispatch


class AsyncIterator:
    """Helper class to create async iterators for mocking."""
    
    def __init__(self, items: List[Any]):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


@pytest.fixture
def mock_session():
    """Create a mock Neo4j session."""
    session = AsyncMock(spec=AsyncSession)
    session.run = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_handle_search_success(mock_session):
    """Test successful search handling."""
    # Mock search results
    mock_session.run.return_value = AsyncIterator([
        {
            "node": {
                "id": "1",
                "name": "Python",
                "type": "Skill",
                "description": "Python programming language"
            }
        }
    ])

    result = await handle_search(
        session=mock_session,
        query="Python",
        limit=10
    )

    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["node"]["name"] == "Python"


@pytest.mark.asyncio
async def test_handle_search_empty_query(mock_session):
    """Test search handling with empty query."""
    with pytest.raises(HTTPException) as exc_info:
        await handle_search(session=mock_session, query="", limit=10)
    assert exc_info.value.status_code == 400
    assert "Query cannot be empty" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_handle_search_database_error(mock_session):
    """Test search handling with database error."""
    mock_session.run.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await handle_search(session=mock_session, query="Python", limit=10)
    assert exc_info.value.status_code == 500
    assert "Database error" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_handle_tool_dispatch_success(mock_session: AsyncMock) -> None:
    """Test successful tool dispatch handling."""
    with patch("skill_sphere_mcp.tools.dispatcher.dispatch_tool") as mock_dispatch:
        mock_dispatch.return_value = {
            "match_score": 0.0,
            "matching_skills": [],
            "skill_gaps": ["Python"]
        }

        result = await handle_tool_dispatch(
            session=mock_session,
            tool_name="skill.match_role",  # Use a valid tool name
            parameters={"required_skills": ["Python"], "years_experience": {"Python": 5}}
        )
        assert result["result"] == "success"
        assert result["data"] == {
            "match_score": 0.0,
            "matching_skills": [],
            "skill_gaps": ["Python"]
        }


@pytest.mark.asyncio
async def test_handle_tool_dispatch_missing_name(mock_session: AsyncMock) -> None:
    """Test tool dispatch handling with missing tool name."""
    with pytest.raises(HTTPException) as exc_info:
        await handle_tool_dispatch(session=mock_session, tool_name="", parameters={})
    assert exc_info.value.status_code == 422  # Changed from 400 to 422
    assert exc_info.value.detail == "Tool name is required"  # Updated error message


@pytest.mark.asyncio
async def test_handle_get_entity_success(mock_session):
    """Test successful entity retrieval."""
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value={
        "n": {
            "id": "1",
            "name": "Test Entity",
            "type": "Skill",
            "description": "Test description"
        }
    })
    mock_session.run.return_value = mock_result

    result = await handle_get_entity(session=mock_session, entity_id="1")

    assert result["id"] == "1"
    assert result["name"] == "Test Entity"
    assert result["type"] == "Skill"


@pytest.mark.asyncio
async def test_handle_get_entity_not_found(mock_session):
    """Test entity retrieval for non-existent entity."""
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value=None)
    mock_session.run.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await handle_get_entity(session=mock_session, entity_id="nonexistent")
    assert exc_info.value.status_code == 404
    assert "Entity not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_handle_list_resources():
    """Test handle_list_resources function."""
    mock_session = AsyncMock()
    result = await handle_list_resources(mock_session)
    assert result == ["nodes", "relationships", "search"]


@pytest.mark.asyncio
async def test_handle_get_resource_valid():
    """Test valid resource retrieval."""
    result = await get_resource(resource_type="nodes")
    assert isinstance(result, dict)
    assert "type" in result
    assert "description" in result


@pytest.mark.asyncio
async def test_handle_get_resource_invalid():
    """Test invalid resource retrieval."""
    with pytest.raises(HTTPException) as exc_info:
        await get_resource(resource_type="invalid")
    assert exc_info.value.status_code == 400
    assert "Invalid resource type" in str(exc_info.value.detail) 