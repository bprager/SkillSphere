"""Tests for API routes."""

# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from fastapi import HTTPException
from neo4j import AsyncSession

from skill_sphere_mcp.api.routes import create_skill
from skill_sphere_mcp.api.routes import get_skills
from skill_sphere_mcp.api.routes import health_check
from skill_sphere_mcp.models.skill import Skill


# Test data
MOCK_SKILL_NAME = "Python"
MOCK_SKILLS = [{"name": "Python"}, {"name": "FastAPI"}]

# HTTP status codes
HTTP_INTERNAL_ERROR = 500


class AsyncRecordIterator:
    """Async iterator for mock Neo4j records."""

    def __init__(self, records: list[dict]):
        self.records = records
        self.index = 0

    def __aiter__(self) -> "AsyncRecordIterator":
        return self

    async def __anext__(self) -> dict:
        if self.index >= len(self.records):
            raise StopAsyncIteration
        record = self.records[self.index]
        self.index += 1
        return record


@pytest_asyncio.fixture
async def mock_session():
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test health check endpoint."""
    response = await health_check()
    assert isinstance(response, dict)
    assert response == {"status": "healthy"}


@pytest.mark.asyncio
async def test_get_skills_success(mock_session: AsyncMock) -> None:
    """Test successful skills retrieval."""
    # Mock the Neo4j result
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = [
        {"s": {"name": skill["name"]}} for skill in MOCK_SKILLS
    ]
    mock_session.run.return_value = mock_result

    skills = await get_skills(mock_session)
    assert isinstance(skills, list)
    assert len(skills) == len(MOCK_SKILLS)
    assert all(hasattr(skill, "name") for skill in skills)
    assert [skill.name for skill in skills] == [skill["name"] for skill in MOCK_SKILLS]

    # Verify Neo4j query was called correctly
    mock_session.run.assert_called_once_with("MATCH (s:Skill) RETURN s")


@pytest.mark.asyncio
async def test_get_skills_empty(mock_session: AsyncMock) -> None:
    """Test skills retrieval with empty result."""
    # Mock empty result
    mock_result = AsyncMock()
    mock_result.__aiter__ = lambda self: AsyncRecordIterator([])
    mock_session.run.return_value = mock_result

    skills = await get_skills(mock_session)
    assert isinstance(skills, list)
    assert len(skills) == 0


@pytest.mark.asyncio
async def test_get_skills_error(mock_session: AsyncMock) -> None:
    """Test skills retrieval with database error."""
    mock_session.run.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await get_skills(mock_session)
    assert exc_info.value.status_code == HTTP_INTERNAL_ERROR
    assert exc_info.value.detail == "Failed to fetch skills"


@pytest.mark.asyncio
async def test_create_skill_success(mock_session: AsyncMock) -> None:
    """Test successful skill creation."""
    # Mock the Neo4j result
    mock_result = AsyncMock()
    mock_result.single.return_value = {"s": {"name": MOCK_SKILL_NAME}}
    mock_session.run.return_value = mock_result

    skill = Skill(name=MOCK_SKILL_NAME)
    response = await create_skill(skill, mock_session)
    assert isinstance(response, Skill)
    assert response.name == MOCK_SKILL_NAME

    # Verify Neo4j query was called correctly
    mock_session.run.assert_called_once_with(
        "CREATE (s:Skill $skill) RETURN s",
        skill={"name": MOCK_SKILL_NAME},
    )


@pytest.mark.asyncio
async def test_create_skill_no_result(mock_session: AsyncMock) -> None:
    """Test skill creation with no result."""
    # Mock empty result
    mock_result = AsyncMock()
    mock_result.single.return_value = None
    mock_session.run.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await create_skill(MOCK_SKILL_NAME, mock_session)
    assert exc_info.value.status_code == HTTP_INTERNAL_ERROR
    assert exc_info.value.detail == "Failed to create skill"


@pytest.mark.asyncio
async def test_create_skill_error(mock_session: AsyncMock) -> None:
    """Test skill creation with database error."""
    mock_session.run.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await create_skill(MOCK_SKILL_NAME, mock_session)
    assert exc_info.value.status_code == HTTP_INTERNAL_ERROR
    assert exc_info.value.detail == "Failed to create skill"
