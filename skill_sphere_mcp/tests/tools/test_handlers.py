"""Tests for tool handlers."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
from fastapi import HTTPException
from neo4j import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from skill_sphere_mcp.graph.skill_matching import MatchResult, SkillMatch
from skill_sphere_mcp.tools.handlers import (explain_match, generate_cv,
                                             graph_search, match_role)

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


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_skill_matcher() -> AsyncMock:
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


@pytest.mark.asyncio
async def test_match_role_success(
    mock_session: AsyncMock, mock_skill_matcher: AsyncMock
) -> None:
    """Test successful skill matching."""
    # Setup mock session response
    mock_result = AsyncMock()
    mock_result.__aiter__.return_value = [
        {"name": "Python", "years": 5},
        {"name": "FastAPI", "years": 3},
    ]
    mock_session.run.return_value = mock_result

    # Test with patch
    with patch("skill_sphere_mcp.tools.handlers.skill_matcher", mock_skill_matcher):
        result = await match_role(
            {
                "required_skills": MOCK_REQUIRED_SKILLS,
                "years_experience": MOCK_YEARS_EXPERIENCE,
            },
            mock_session,
        )

        assert result["match_score"] == pytest.approx(0.85)
        assert "Python" in [s["name"] for s in result["matching_skills"]]
        assert "Kafka" in result["skill_gaps"]


@pytest.mark.asyncio
async def test_match_role_no_skills(mock_session: AsyncMock) -> None:
    """Test skill matching with no skills provided."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role({"required_skills": [], "years_experience": {}}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_explain_match_success(mock_session: AsyncMock) -> None:
    """Test successful match explanation."""
    # Setup mock session response
    mock_result = AsyncMock()
    mock_result.single.return_value = {
        "s": {"name": "Python"},
        "evidence": [
            {
                "type": "HAS_EXPERIENCE",
                "target": {"name": "FastAPI"},
                "properties": {"years": 3},
            }
        ],
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


@pytest.mark.asyncio
async def test_explain_match_invalid_params(mock_session: AsyncMock) -> None:
    """Test match explanation with invalid parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match({}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_generate_cv_success(mock_session: AsyncMock) -> None:
    """Test successful CV generation."""
    result = await generate_cv(
        {"target_keywords": ["Python"], "format": "markdown"}, mock_session
    )
    assert result["format"] == "markdown"
    assert "content" in result


@pytest.mark.asyncio
async def test_generate_cv_invalid_format(mock_session: AsyncMock) -> None:
    """Test CV generation with invalid format."""
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {"target_keywords": ["Python"], "format": "invalid"}, mock_session
        )
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_graph_search_success(mock_session: AsyncMock) -> None:
    """Test successful graph search."""
    # Mock MODEL.encode
    with patch("skill_sphere_mcp.tools.handlers.MODEL") as mock_model:
        mock_model.encode.return_value = MOCK_EMBEDDING

        # Mock embeddings.search
        with patch("skill_sphere_mcp.tools.handlers.embeddings") as mock_embeddings:
            mock_embeddings.search = AsyncMock(
                return_value=[
                    {
                        "node_id": "1",
                        "score": 0.9,
                        "labels": ["Skill"],
                        "properties": {"name": "Python"},
                    }
                ]
            )

            result = await graph_search(
                {"query": "Python developer", "top_k": 5}, mock_session
            )

            assert "results" in result
            assert len(result["results"]) == 1
            assert result["results"][0]["node_id"] == "1"


@pytest.mark.asyncio
async def test_graph_search_no_query(mock_session: AsyncMock) -> None:
    """Test graph search with no query."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_graph_search_invalid_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with invalid top_k."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({"query": "Python", "top_k": 0}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_graph_search_fallback_random(mock_session: AsyncMock) -> None:
    """Test graph search fallback to random embedding when MODEL is None."""
    # Mock MODEL as None
    with patch("skill_sphere_mcp.tools.handlers.MODEL", None):
        # Mock embeddings.search
        with patch("skill_sphere_mcp.tools.handlers.embeddings") as mock_embeddings:
            mock_embeddings.search = AsyncMock(
                return_value=[
                    {
                        "node_id": "1",
                        "score": 0.9,
                        "labels": ["Skill"],
                        "properties": {"name": "Python"},
                    }
                ]
            )

            result = await graph_search(
                {"query": "Python developer", "top_k": 5}, mock_session
            )

            assert "results" in result
            assert len(result["results"]) == 1
            # Verify random embedding was used
            mock_embeddings.search.assert_called_once()
            call_args = mock_embeddings.search.call_args
            assert isinstance(call_args[0][1], np.ndarray)
            assert call_args[0][1].shape == (128,)
