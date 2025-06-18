"""Tests for MCP models."""

import pytest

from pydantic import ValidationError

from skill_sphere_mcp.api.mcp.models import EntityResponse
from skill_sphere_mcp.api.mcp.models import ResourceResponse
from skill_sphere_mcp.api.mcp.models import SearchRequest
from skill_sphere_mcp.api.mcp.models import SearchResponse
from skill_sphere_mcp.api.mcp.models import ToolDispatchRequest
from skill_sphere_mcp.api.mcp.models import ToolDispatchResponse


def test_search_request_validation():
    """Test SearchRequest model validation."""
    # Valid request
    request = SearchRequest(query="Python", limit=10)
    assert request.query == "Python"
    assert request.limit == 10

    # Invalid query
    with pytest.raises(ValidationError) as exc_info:
        SearchRequest(query="", limit=10)
    assert "at least 1 character" in str(exc_info.value)

    # Invalid limit
    with pytest.raises(ValidationError) as exc_info:
        SearchRequest(query="Python", limit=0)
    assert "greater than 0" in str(exc_info.value)

    # Default limit
    request = SearchRequest(query="Python")
    assert request.limit == 20  # Default value


def test_tool_dispatch_request_validation():
    """Test ToolDispatchRequest model validation."""
    # Valid request
    request = ToolDispatchRequest(
        tool_name="test.tool",
        parameters={"key": "value"}
    )
    assert request.tool_name == "test.tool"
    assert request.parameters == {"key": "value"}

    # Missing tool name
    with pytest.raises(ValidationError) as exc_info:
        ToolDispatchRequest(tool_name="", parameters={})
    assert "at least 1 character" in str(exc_info.value)

    # Invalid parameters type
    with pytest.raises(ValidationError) as exc_info:
        ToolDispatchRequest(tool_name="test.tool", parameters="not_a_dict")
    assert "valid dictionary" in str(exc_info.value)


def test_entity_response_validation():
    """Test EntityResponse model validation."""
    # Valid response
    response = EntityResponse(
        id="1",
        name="Test Entity",
        type="Skill",
        description="Test description",
        properties={"key": "value"},
        relationships=[
            {
                "type": "RELATES_TO",
                "target": {"id": "2", "name": "Related Entity"}
            }
        ]
    )
    assert response.id == "1"
    assert response.name == "Test Entity"
    assert response.type == "Skill"
    assert response.description == "Test description"
    assert response.properties == {"key": "value"}
    assert len(response.relationships) == 1

    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        EntityResponse(id="1")
    assert "name" in str(exc_info.value)
    assert "type" in str(exc_info.value)


def test_resource_response_validation():
    """Test ResourceResponse model validation."""
    # Valid response
    response = ResourceResponse(
        type="nodes",
        description="Graph nodes",
        properties=["id", "name", "type"],
        relationships=["RELATES_TO", "BELONGS_TO"]
    )
    assert response.type == "nodes"
    assert response.description == "Graph nodes"
    assert "id" in response.properties
    assert "RELATES_TO" in response.relationships

    # Missing required fields
    with pytest.raises(ValidationError) as exc_info:
        ResourceResponse(type="nodes")
    assert "description" in str(exc_info.value)


def test_search_response_validation():
    """Test SearchResponse model validation."""
    # Valid response
    response = SearchResponse(
        results=[
            {
                "node": {
                    "id": "1",
                    "name": "Python",
                    "type": "Skill"
                },
                "score": 0.95
            }
        ],
        total=1
    )
    assert len(response.results) == 1
    assert response.total == 1
    assert response.results[0]["node"]["name"] == "Python"
    assert response.results[0]["score"] == 0.95

    # Empty results
    response = SearchResponse(results=[], total=0)
    assert len(response.results) == 0
    assert response.total == 0


def test_tool_dispatch_response_validation():
    """Test ToolDispatchResponse model validation."""
    # Valid response
    response = ToolDispatchResponse(
        result="success",
        data={"key": "value"},
        message="Operation completed successfully"
    )
    assert response.result == "success"
    assert response.data == {"key": "value"}
    assert response.message == "Operation completed successfully"

    # Error response
    response = ToolDispatchResponse(
        result="error",
        data={"error": "Something went wrong"},
        message="Operation failed"
    )
    assert response.result == "error"
    assert "error" in response.data
    assert response.message == "Operation failed" 