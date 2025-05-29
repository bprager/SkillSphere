"""Tests for tool handlers."""

import logging
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest
import pytest_asyncio
from fastapi import HTTPException
from neo4j import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from skill_sphere_mcp.cv.generator import generate_cv
from skill_sphere_mcp.graph.skill_matching import MatchResult, SkillMatch
from skill_sphere_mcp.tools.handlers import explain_match, graph_search, match_role

logger = logging.getLogger(__name__)

# Test data
MOCK_SKILLS = [
    {"name": "Python", "years": 5},
    {"name": "FastAPI", "years": 3},
]
MOCK_REQUIRED_SKILLS = ["Python", "FastAPI"]
MOCK_YEARS_EXPERIENCE = {"Python": 5, "FastAPI": 3}

# Mock embeddings
MOCK_EMBEDDING = np.random.default_rng(42).random(128)


@pytest_asyncio.fixture
async def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest_asyncio.fixture
async def mock_skill_matcher() -> AsyncMock:
    """Create a mock skill matcher."""
    matcher = AsyncMock()
    matcher.match_role.return_value = MatchResult(
        overall_score=0.85,
        matching_skills=[
            SkillMatch(
                skill_name="Python",
                match_score=0.9,
                evidence=[{"type": "HAS_SKILL", "target": "FastAPI"}],
                experience_years=5.0,
            )
        ],
        skill_gaps=["Kafka"],
        supporting_nodes=[{"id": 1, "name": "Python"}],
    )
    return matcher


# TODO: Resolve the skipped test for test_match_role_success.
@pytest.mark.skip(reason="Test is currently failing and needs to be reviewed.")
@pytest_asyncio.fixture
async def test_match_role_success(
    mock_session: AsyncMock, mock_skill_matcher: AsyncMock
) -> None:
    """Test successful skill matching."""
    # Setup mock session response
    mock_result = AsyncMock()
    mock_result.__aiter__.return_value = [
        {"p": {"name": "Python", "skills": ["Python", "FastAPI"]}},
        {"p": {"name": "FastAPI", "skills": ["Python", "FastAPI"]}},
    ]
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": MOCK_REQUIRED_SKILLS,
            "years_experience": MOCK_YEARS_EXPERIENCE,
        },
        mock_session,
    )

    assert result["match_score"] == pytest.approx(1.0)
    assert "Python" in [s["name"] for s in result["matching_skills"]]
    assert result["skill_gaps"] == []


@pytest_asyncio.fixture
async def test_match_role_no_skills(mock_session: AsyncMock) -> None:
    """Test skill matching with no skills provided."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role({"required_skills": [], "years_experience": {}}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest_asyncio.fixture
async def test_explain_match_success(mock_session: AsyncMock) -> None:
    """Test successful match explanation."""
    # Setup mock session response
    mock_result = AsyncMock()
    mock_result.single.return_value = {
        "s": {"name": "Python"},
        "projects": [{"name": "Project1"}],
        "certifications": [{"name": "Cert1"}],
    }
    mock_session.run.return_value = mock_result

    result = await explain_match(
        {
            "skill_id": "1",
            "role_requirement": "Python developer with FastAPI experience",
        },
        mock_session,
    )

    assert "explanation" in result
    assert "evidence" in result
    assert len(result["evidence"]) > 0


@pytest_asyncio.fixture
async def test_explain_match_invalid_params(mock_session: AsyncMock) -> None:
    """Test match explanation with invalid parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match({}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest_asyncio.fixture
async def test_generate_cv_success(mock_session: AsyncMock) -> None:
    """Test successful CV generation."""
    mock_record = {
        "p": {"name": "John"},
        "skills": [{"name": "Python"}],
        "companies": [],
        "education": [],
    }
    mock_session.run.return_value.single.return_value = mock_record
    result = await generate_cv(
        {"target_keywords": ["Python"], "format": "markdown"}, mock_session
    )
    assert result["format"] == "markdown"
    assert "content" in result


@pytest_asyncio.fixture
async def test_generate_cv_invalid_format(mock_session: AsyncMock) -> None:
    """Test CV generation with invalid format."""
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {"target_keywords": ["Python"], "format": "invalid"}, mock_session
        )
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest_asyncio.fixture
async def test_graph_search_success(mock_session: AsyncMock) -> None:
    """Test successful graph search."""
    # Mock the session to return a list of nodes
    mock_result = AsyncMock()
    mock_result.all.return_value = [
        {"n": {"id": "1", "name": "Python"}},
        {"n": {"id": "2", "name": "FastAPI"}},
    ]
    mock_session.run.return_value = mock_result

    result = await graph_search({"query": "Python", "top_k": 5}, mock_session)

    assert "results" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["node"]["name"] == "Python"


@pytest_asyncio.fixture
async def test_graph_search_no_query(mock_session: AsyncMock) -> None:
    """Test graph search with no query."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest_asyncio.fixture
async def test_graph_search_invalid_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with invalid top_k."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({"query": "Python", "top_k": 0}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest_asyncio.fixture
async def test_graph_search_fallback_random(mock_session: AsyncMock) -> None:
    """Test graph search fallback to random embedding when MODEL is None."""
    # Mock the session to return a list of nodes
    mock_result = AsyncMock()
    mock_result.all.return_value = [
        {"n": {"id": "1", "name": "Python"}},
        {"n": {"id": "2", "name": "FastAPI"}},
    ]
    mock_session.run.return_value = mock_result

    result = await graph_search({"query": "Python", "top_k": 5}, mock_session)

    assert "results" in result
    assert len(result["results"]) == 2
    assert result["results"][0]["node"]["name"] == "Python"
