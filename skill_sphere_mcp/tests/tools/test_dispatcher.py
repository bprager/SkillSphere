"""Tests for tool dispatcher."""

from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import HTTPException, status
from neo4j import AsyncSession
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from skill_sphere_mcp.tools.dispatcher import (
    _validate_explain_match_params,
    _validate_generate_cv_params,
    _validate_graph_search_params,
    _validate_match_role_params,
    dispatch_tool,
)

# Test data
MOCK_SKILLS = ["Python", "FastAPI"]
MOCK_YEARS = {"Python": 5, "FastAPI": 3}


@pytest_asyncio.fixture
def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


def test_validate_match_role_params() -> None:
    """Test validation of match role parameters."""
    # Valid parameters
    _validate_match_role_params(
        {
            "required_skills": MOCK_SKILLS,
            "years_experience": MOCK_YEARS,
        }
    )

    # Invalid parameters
    with pytest.raises(HTTPException) as exc_info:
        _validate_match_role_params({})
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    with pytest.raises(HTTPException) as exc_info:
        _validate_match_role_params({"required_skills": []})
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_validate_explain_match_params() -> None:
    """Test validation of explain match parameters."""
    # Valid parameters
    _validate_explain_match_params(
        {
            "skill_id": "1",
            "role_requirement": "Python developer",
        }
    )

    # Invalid parameters
    with pytest.raises(HTTPException) as exc_info:
        _validate_explain_match_params({})
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_validate_generate_cv_params() -> None:
    """Test validation of CV generation parameters."""
    # Valid parameters
    _validate_generate_cv_params(
        {
            "profile_id": "123",
            "target_keywords": MOCK_SKILLS,
            "format": "markdown",
        }
    )

    # Invalid parameters
    with pytest.raises(HTTPException) as exc_info:
        _validate_generate_cv_params(
            {
                "target_keywords": MOCK_SKILLS,
                "format": "markdown",
            }
        )
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.detail == "Profile ID is required"

    with pytest.raises(HTTPException) as exc_info:
        _validate_generate_cv_params(
            {
                "target_keywords": MOCK_SKILLS,
                "format": "invalid",
            }
        )
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY


def test_validate_graph_search_params() -> None:
    """Test validation of graph search parameters."""
    # Valid parameters
    _validate_graph_search_params(
        {
            "query": "Python developer",
            "top_k": 5,
        }
    )

    # Invalid parameters
    with pytest.raises(HTTPException) as exc_info:
        _validate_graph_search_params({})
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    with pytest.raises(HTTPException) as exc_info:
        _validate_graph_search_params(
            {
                "query": "Python",
                "top_k": 0,
            }
        )
    assert exc_info.value.status_code == HTTP_422_UNPROCESSABLE_ENTITY


@pytest_asyncio.fixture
async def test_dispatch_tool_success(mock_session: AsyncMock) -> None:
    """Test successful tool dispatch."""
    # Mock the handler functions
    with patch("skill_sphere_mcp.tools.dispatcher.match_role") as mock_match_role:
        mock_match_role.return_value = {
            "match_score": 0.85,
            "matching_skills": [{"name": "Python"}],
            "skill_gaps": [],
        }

        result = await dispatch_tool(
            "skill.match_role",
            {
                "required_skills": MOCK_SKILLS,
                "years_experience": MOCK_YEARS,
            },
            mock_session,
        )

        assert result["match_score"] == pytest.approx(0.85)
        assert len(result["matching_skills"]) == 1


@pytest_asyncio.fixture
async def test_dispatch_tool_invalid_name(mock_session: AsyncMock) -> None:
    """Test tool dispatch with invalid tool name."""
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool("invalid.tool", {}, mock_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest_asyncio.fixture
async def test_dispatch_tool_invalid_params(mock_session: AsyncMock) -> None:
    """Test tool dispatch with invalid parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await dispatch_tool("skill.match_role", {}, mock_session)
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest_asyncio.fixture
async def test_dispatch_tool_handler_error(mock_session: AsyncMock) -> None:
    """Test tool dispatch with handler error."""
    with patch("skill_sphere_mcp.tools.dispatcher.match_role") as mock_match_role:
        mock_match_role.side_effect = Exception("Handler error")

        with pytest.raises(HTTPException) as exc_info:
            await dispatch_tool(
                "skill.match_role",
                {
                    "required_skills": MOCK_SKILLS,
                    "years_experience": MOCK_YEARS,
                },
                mock_session,
            )
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
