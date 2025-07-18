"""Tests for database utility functions."""

from collections import UserDict
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException, status
from neo4j import AsyncSession

from skill_sphere_mcp.db.utils import get_entity_by_id


@pytest.mark.asyncio
async def test_get_entity_by_id_invalid_id():
    """Test get_entity_by_id with invalid ID."""
    mock_session = AsyncMock(spec=AsyncSession)

    # Test with empty string
    with pytest.raises(HTTPException) as exc_info:
        await get_entity_by_id(mock_session, "")
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid entity ID" in str(exc_info.value.detail)

    # Test with non-string ID
    with pytest.raises(HTTPException) as exc_info:
        await get_entity_by_id(mock_session, 123)  # type: ignore
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid entity ID" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_entity_by_id_not_found():
    """Test get_entity_by_id when entity is not found."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock()
    mock_result.single.return_value = None
    mock_session.run.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await get_entity_by_id(mock_session, "nonexistent")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Entity not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_entity_by_id_success():
    """Test successful entity retrieval with relationships."""
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock Neo4j node and relationships
    mock_node = UserDict({"name": "Test Entity", "description": "Test Description"})
    mock_target = UserDict({"id": "target1", "name": "Target Entity"})

    mock_record = {
        "n": mock_node,
        "labels": ["Skill"],
        "relationships": [
            {"type": "RELATES_TO", "target": mock_target, "target_labels": ["Skill"]}
        ],
    }

    mock_result = AsyncMock()
    mock_result.single.return_value = mock_record
    mock_session.run.return_value = mock_result

    result = await get_entity_by_id(mock_session, "test123")

    assert result["id"] == "test123"
    assert result["type"] == "Skill"
    assert result["name"] == "Test Entity"
    assert result["description"] == "Test Description"
    assert len(result["relationships"]) == 1
    assert result["relationships"][0]["type"] == "RELATES_TO"
    assert result["relationships"][0]["target"]["id"] == "target1"
    assert result["relationships"][0]["target_type"] == "Skill"


@pytest.mark.asyncio
async def test_get_entity_by_id_database_error():
    """Test get_entity_by_id with database error."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.run.side_effect = Exception("Database connection error")

    with pytest.raises(HTTPException) as exc_info:
        await get_entity_by_id(mock_session, "test123")
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_entity_by_id_null_relationships():
    """Test get_entity_by_id with null relationships."""
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock Neo4j node with null relationships
    mock_node = UserDict({"name": "Test Entity"})

    mock_record = {
        "n": mock_node,
        "labels": ["Skill"],
        "relationships": [{"type": None, "target": None, "target_labels": None}],
    }

    mock_result = AsyncMock()
    mock_result.single.return_value = mock_record
    mock_session.run.return_value = mock_result

    result = await get_entity_by_id(mock_session, "test123")

    assert result["id"] == "test123"
    assert result["type"] == "Skill"
    assert result["name"] == "Test Entity"
    assert (
        len(result["relationships"]) == 0
    )  # Null relationships should be filtered out
