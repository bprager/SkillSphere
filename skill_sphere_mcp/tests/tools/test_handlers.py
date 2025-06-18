"""Tests for the tool handlers."""

import logging

from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pytest
import pytest_asyncio

from fastapi import HTTPException
from neo4j import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST
from tests.constants import DEFAULT_TEST_LIMIT
from tests.constants import DEFAULT_TEST_TOP_K
from tests.constants import HTTP_BAD_REQUEST
from tests.constants import HTTP_NOT_FOUND

from skill_sphere_mcp.api.mcp.handlers import explain_match
from skill_sphere_mcp.api.mcp.handlers import graph_search
from skill_sphere_mcp.api.mcp.handlers import match_role
from skill_sphere_mcp.cv.generator import generate_cv
from skill_sphere_mcp.graph.skill_matching import MatchResult
from skill_sphere_mcp.graph.skill_matching import SkillMatch


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

EXPECTED_RESULTS_COUNT = 2


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


@pytest.mark.asyncio
async def test_match_role_success(mock_session: AsyncMock) -> None:
    """Test successful skill matching."""
    # Setup mock session response
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(
        return_value=[
            {
                "p": {
                    "id": "1",
                    "name": "Test Person",
                    "skills": ["Python", "FastAPI"],
                    "experience": {"Python": 5, "FastAPI": 3},
                }
            }
        ]
    )
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": ["Python"],
            "years_experience": {"Python": 3},
        },
        mock_session,
    )
    assert "match_score" in result
    assert result["match_score"] == 1.0
    assert "matching_skills" in result
    assert len(result["matching_skills"]) == 1
    assert "skill_gaps" in result
    assert len(result["skill_gaps"]) == 0


@pytest.mark.asyncio
async def test_match_role_no_skills(mock_session: AsyncMock) -> None:
    """Test skill matching with no skills provided."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role({"required_skills": [], "years_experience": {}}, mock_session)
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_explain_match_success(mock_session: AsyncMock) -> None:
    """Test successful explain match."""
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(
        return_value={
            "s": {"id": "1", "name": "Python"},
            "projects": [
                {"id": "p1", "name": "Project A", "description": "Python project"}
            ],
            "certifications": [
                {
                    "id": "c1",
                    "name": "Python Cert",
                    "description": "Python certification",
                }
            ],
        }
    )
    mock_session.run.return_value = mock_result

    result = await explain_match(
        {
            "skill_id": "1",
            "role_requirement": "Python Developer",
        },
        mock_session,
    )
    assert "explanation" in result
    assert "evidence" in result
    assert len(result["evidence"]) == 2
    assert any(e["type"] == "project" for e in result["evidence"])
    assert any(e["type"] == "certification" for e in result["evidence"])


@pytest.mark.asyncio
async def test_explain_match_missing_params(mock_session: AsyncMock) -> None:
    """Test explain match with missing parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match({}, mock_session)
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_explain_match_skill_not_found(mock_session: AsyncMock) -> None:
    """Test explain match with non-existent skill."""
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(return_value=None)
    mock_session.run.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await explain_match(
            {
                "skill_id": "999",
                "role_requirement": "Python Developer",
            },
            mock_session,
        )
    assert exc_info.value.status_code == 404
    assert "Skill 999 not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_generate_cv_invalid_format(mock_session: AsyncMock) -> None:
    """Test CV generation with invalid format."""
    with pytest.raises(HTTPException) as exc_info:
        await generate_cv(
            {
                "profile_id": "123",
                "target_keywords": ["Python"],
                "format": "invalid"
            },
            mock_session
        )
    assert exc_info.value.status_code == 422
    assert "Validation error" in str(exc_info.value.detail)
    assert "format" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_graph_search_success(mock_session: AsyncMock) -> None:
    """Test successful graph search."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(
        return_value=[
            {
                "n": {
                    "id": "1",
                    "name": "Python",
                    "type": "Skill",
                    "description": "Python programming language",
                    "labels": ["Skill"],
                    "properties": {
                        "name": "Python",
                        "description": "Python programming language",
                    },
                }
            }
        ]
    )
    mock_session.run.return_value = mock_result

    result = await graph_search(
        {
            "query": "Python",
            "top_k": 5,
        },
        mock_session,
    )
    assert "results" in result
    assert len(result["results"]) == 1
    assert "node" in result["results"][0]
    assert result["results"][0]["node"]["name"] == "Python"


@pytest.mark.asyncio
async def test_graph_search_missing_query(mock_session: AsyncMock) -> None:
    """Test graph search with missing query."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({}, mock_session)
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_graph_search_invalid_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with invalid top_k."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search(
            {
                "query": "test",
                "top_k": 0,
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_match_role_missing_skills(mock_session: AsyncMock) -> None:
    """Test role matching with missing required skills."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "years_experience": {"Python": 3},
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_match_role_invalid_experience(mock_session: AsyncMock) -> None:
    """Test match role with invalid years_experience."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": "invalid",  # Should be a dict
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422
    assert "years_experience must be a dictionary" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_invalid_experience_type(mock_session: AsyncMock) -> None:
    """Test match role with invalid years_experience type."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": {"Python": "invalid"},  # Should be int
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422
    assert "must be an integer" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_invalid_experience_value(mock_session: AsyncMock) -> None:
    """Test match role with invalid years_experience value."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": {"Python": -1},  # Should be positive
            },
            mock_session,
        )
    assert exc_info.value.status_code == 422
    assert "must be positive" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_partial_match(mock_session: AsyncMock) -> None:
    """Test role matching with partial skill matches."""
    # Mock the session to return a profile with only some required skills
    mock_result = AsyncMock()
    # The handler expects all required skills to be present in the profile for a match
    # So, if only one skill is present, match_score should be 0.0
    mock_result.all = AsyncMock(return_value=[])  # No full matches
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": ["Python", "Django"],
            "years_experience": {"Python": 3, "Django": 2},
        },
        mock_session,
    )

    assert result["match_score"] == 0.0
    assert isinstance(result["skill_gaps"], list)
    assert isinstance(result["matching_skills"], list)


@pytest.mark.asyncio
async def test_explain_match_empty_evidence(mock_session: AsyncMock) -> None:
    """Test explain match with no projects or certifications."""
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(
        return_value={
            "s": {"id": "1", "name": "Python"},
            "projects": [],
            "certifications": [],
        }
    )
    mock_session.run.return_value = mock_result

    result = await explain_match(
        {"skill_id": "1", "role_requirement": "Python Developer"},
        mock_session,
    )

    assert "explanation" in result
    assert "evidence" in result
    assert len(result["evidence"]) == 0
    assert "based on 0 projects and 0 certifications" in result["explanation"]


@pytest.mark.asyncio
async def test_explain_match_multiple_evidence(mock_session: AsyncMock) -> None:
    """Test explain match with multiple pieces of evidence."""
    mock_result = AsyncMock()
    mock_result.single = AsyncMock(
        return_value={
            "s": {"id": "1", "name": "Python"},
            "projects": [
                {"id": "p1", "name": "Project A"},
                {"id": "p2", "name": "Project B"},
                {"id": "p3", "name": "Project C"},
            ],
            "certifications": [
                {"id": "c1", "name": "Cert A"},
                {"id": "c2", "name": "Cert B"},
            ],
        }
    )
    mock_session.run.return_value = mock_result

    result = await explain_match(
        {"skill_id": "1", "role_requirement": "Python Developer"},
        mock_session,
    )

    assert len(result["evidence"]) == 5
    assert any("Project A" in str(e["description"]) for e in result["evidence"])
    assert any("Cert A" in str(e["description"]) for e in result["evidence"])


@pytest.mark.asyncio
async def test_explain_match_invalid_skill_id(mock_session: AsyncMock) -> None:
    """Test explain match with invalid skill ID format."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match(
            {"skill_id": "invalid", "role_requirement": "Python Developer"},
            mock_session,
        )
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_graph_search_empty_results(mock_session: AsyncMock) -> None:
    """Test graph search with no matching results."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(return_value=[])
    mock_session.run.return_value = mock_result

    result = await graph_search({"query": "nonexistent", "top_k": 5}, mock_session)
    assert "results" in result
    assert len(result["results"]) == 0


@pytest.mark.asyncio
async def test_graph_search_special_characters(mock_session: AsyncMock) -> None:
    """Test graph search with special characters in query."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(
        return_value=[
            {"n": {"id": "1", "name": "C++", "description": "Programming language"}}
        ]
    )
    mock_session.run.return_value = mock_result

    result = await graph_search({"query": "C++", "top_k": 5}, mock_session)
    assert "results" in result
    assert len(result["results"]) > 0
    assert result["results"][0]["node"]["name"] == "C++"


@pytest.mark.asyncio
async def test_graph_search_large_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with a large top_k value."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(
        return_value=[{"n": {"id": str(i), "name": f"Node {i}"}} for i in range(100)]
    )
    mock_session.run.return_value = mock_result

    result = await graph_search({"query": "Node", "top_k": 100}, mock_session)
    assert "results" in result
    assert len(result["results"]) == 100


@pytest.mark.asyncio
async def test_match_role_empty_experience(mock_session: AsyncMock) -> None:
    """Test match role with empty years_experience."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(
        return_value=[
            {
                "p": {
                    "name": "Test Person",
                    "skills": ["Python", "FastAPI"],
                    "experience": {},
                }
            }
        ]
    )
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": ["Python", "FastAPI"],
            "years_experience": {},
        },
        mock_session,
    )
    assert "match_score" in result
    assert result["match_score"] == 1.0
    assert len(result["matching_skills"]) == 2
    assert len(result["skill_gaps"]) == 0


@pytest.mark.asyncio
async def test_match_role_nonexistent_skills(mock_session: AsyncMock) -> None:
    """Test match role with non-existent skills."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(return_value=[])
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": ["NonexistentSkill"],
            "years_experience": {"NonexistentSkill": 5},
        },
        mock_session,
    )
    assert "match_score" in result
    assert result["match_score"] == 0.0
    assert len(result["skill_gaps"]) > 0


@pytest.mark.asyncio
async def test_match_role_multiple_profiles(mock_session: AsyncMock) -> None:
    """Test match role with multiple matching profiles."""
    mock_result = AsyncMock()
    mock_result.all = AsyncMock(
        return_value=[
            {
                "p": {
                    "name": "Person 1",
                    "skills": ["Python"],
                    "experience": {"Python": 5},
                }
            },
            {
                "p": {
                    "name": "Person 2",
                    "skills": ["Python"],
                    "experience": {"Python": 3},
                }
            },
        ]
    )
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": ["Python"],
            "years_experience": {"Python": 3},
        },
        mock_session,
    )
    assert "match_score" in result
    assert result["match_score"] == 1.0
    assert len(result["matching_skills"]) == 1
    assert len(result["skill_gaps"]) == 0


@pytest.mark.asyncio
async def test_match_role_empty_skills(mock_session: AsyncMock) -> None:
    """Test match role with empty required_skills list."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role({"required_skills": [], "years_experience": {}}, mock_session)
    assert exc_info.value.status_code == 422
