"""Tests for API routes."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.api.routes import create_skill, get_skills, health_check

# Test data
MOCK_SKILL_NAME = "Python"
MOCK_SKILLS = [{"name": "Python"}, {"name": "FastAPI"}]

# HTTP status codes
HTTP_INTERNAL_ERROR = 500


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test health check endpoint."""
    response = await health_check()
    assert isinstance(response, dict)
    assert response == {"status": "healthy"}


@pytest.mark.asyncio
async def test_get_skills_success(session: AsyncMock) -> None:
    """Test successful skills retrieval."""
    # Mock the Neo4j result
    mock_result = AsyncMock()
    mock_result.__aiter__.return_value = [
        MagicMock(**{"name": skill["name"]}) for skill in MOCK_SKILLS
    ]
    session.run.return_value = mock_result

    skills = await get_skills(session)
    assert isinstance(skills, list)
    assert len(skills) == len(MOCK_SKILLS)
    assert all(isinstance(skill, dict) for skill in skills)
    assert all("name" in skill for skill in skills)
    assert [skill["name"] for skill in skills] == [
        skill["name"] for skill in MOCK_SKILLS
    ]

    # Verify Neo4j query was called correctly
    session.run.assert_called_once_with("MATCH (s:Skill) RETURN s.name as name")


@pytest.mark.asyncio
async def test_get_skills_empty(session: AsyncMock) -> None:
    """Test skills retrieval with empty result."""
    # Mock empty result
    mock_result = AsyncMock()
    mock_result.__aiter__.return_value = []
    session.run.return_value = mock_result

    skills = await get_skills(session)
    assert isinstance(skills, list)
    assert len(skills) == 0


@pytest.mark.asyncio
async def test_get_skills_error(session: AsyncMock) -> None:
    """Test skills retrieval with database error."""
    session.run.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await get_skills(session)
    assert exc_info.value.status_code == HTTP_INTERNAL_ERROR
    assert exc_info.value.detail == "Failed to fetch skills"


@pytest.mark.asyncio
async def test_create_skill_success(session: AsyncMock) -> None:
    """Test successful skill creation."""
    # Mock the Neo4j result
    mock_result = AsyncMock()
    mock_record = MagicMock(**{"name": MOCK_SKILL_NAME})
    mock_result.single.return_value = mock_record
    session.run.return_value = mock_result

    response = await create_skill(MOCK_SKILL_NAME, session)
    assert isinstance(response, dict)
    assert "name" in response
    assert response["name"] == MOCK_SKILL_NAME

    # Verify Neo4j query was called correctly
    session.run.assert_called_once_with(
        "CREATE (s:Skill {name: $name}) RETURN s.name as name",
        name=MOCK_SKILL_NAME,
    )


@pytest.mark.asyncio
async def test_create_skill_no_result(session: AsyncMock) -> None:
    """Test skill creation with no result."""
    # Mock empty result
    mock_result = AsyncMock()
    mock_result.single.return_value = None
    session.run.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await create_skill(MOCK_SKILL_NAME, session)
    assert exc_info.value.status_code == HTTP_INTERNAL_ERROR
    assert exc_info.value.detail == "Failed to create skill"


@pytest.mark.asyncio
async def test_create_skill_error(session: AsyncMock) -> None:
    """Test skill creation with database error."""
    session.run.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await create_skill(MOCK_SKILL_NAME, session)
    assert exc_info.value.status_code == HTTP_INTERNAL_ERROR
    assert exc_info.value.detail == "Failed to create skill"
