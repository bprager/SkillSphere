"""Tests for the tool handlers."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest
import pytest_asyncio
from fastapi import HTTPException
from neo4j import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from skill_sphere_mcp.api.mcp.handlers import explain_match, graph_search, match_role
from skill_sphere_mcp.cv.generator import generate_cv
from skill_sphere_mcp.graph.skill_matching import MatchResult, SkillMatch

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
async def test_match_role_success(
    mock_session: AsyncMock, mock_skill_matcher: AsyncMock
) -> None:
    """Test successful skill matching."""
    # Setup mock session response
    mock_result = AsyncMock()
    mock_result.__aiter__.return_value = [
        {
            "s": {"name": "Python", "skills": ["Python", "FastAPI"]},
            "relationships": [
                {"rel": {"type": "REQUIRES"}, "target": {"id": "1", "name": "Project1"}}
            ],
            "experience_years": [5],
        }
    ]
    mock_session.run.return_value = mock_result

    # Mock the semantic score calculation
    with patch(
        "skill_sphere_mcp.api.mcp.handlers._calculate_semantic_score", return_value=1.0
    ):
        result = await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": {"Python": 3},
            },
            mock_session,
        )

        assert result["match_score"] == pytest.approx(1.0)
        assert len(result["matching_skills"]) == 1
        assert result["matching_skills"][0]["name"] == "Python"
        assert result["skill_gaps"] == []


@pytest.mark.asyncio
async def test_match_role_no_skills(mock_session: AsyncMock) -> None:
    """Test skill matching with no skills provided."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role({"required_skills": [], "years_experience": {}}, mock_session)
    assert exc_info.value.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_explain_match_success(mock_session: AsyncMock) -> None:
    """Test successful skill match explanation."""
    # Mock the session to return skill data with 'evidence' key
    mock_result = AsyncMock()
    mock_result.single.return_value = {
        "s": {
            "id": "1",
            "name": "Python",
            "description": "Programming language",
        },
        "evidence": [
            {"rel": {"type": "USED_IN"}, "target": {"id": "1", "name": "Project A"}},
            {
                "rel": {"type": "CERTIFIED_IN"},
                "target": {"id": "2", "name": "Python Certification"},
            },
        ],
    }
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
    assert "Python" in result["explanation"]
    assert "Python Developer" in result["explanation"]


@pytest.mark.asyncio
async def test_explain_match_missing_params(mock_session: AsyncMock) -> None:
    """Test explain match with missing parameters."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match({}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Invalid parameters" in str(exc_info.value.detail)
    assert "ExplainMatchRequest" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_explain_match_skill_not_found(mock_session: AsyncMock) -> None:
    """Test explain match with non-existent skill."""
    mock_result = AsyncMock()
    mock_result.single.return_value = None
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
    assert "Skill not found" in str(exc_info.value.detail)
    assert "999" in str(exc_info.value.detail)


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
    with pytest.raises(ValueError) as exc_info:
        await generate_cv(
            {"target_keywords": ["Python"], "format": "invalid"}, mock_session
        )
    assert "format" in str(exc_info.value)


@pytest.mark.asyncio
async def test_graph_search_success(mock_session: AsyncMock) -> None:
    """Test successful graph search."""
    # Mock the session to return search results
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = [
        {"n": {"id": "1", "name": "Python", "description": "Programming language"}},
        {"n": {"id": "2", "name": "Django", "description": "Web framework"}},
    ]
    mock_session.run.return_value = mock_result

    # Mock embeddings.search to return results
    with patch("skill_sphere_mcp.api.mcp.handlers.embeddings.search") as mock_search:
        mock_search.return_value = [
            {
                "node_id": "1",
                "name": "Python",
                "description": "Programming language",
                "score": 0.9,
            },
            {
                "node_id": "2",
                "name": "Django",
                "description": "Web framework",
                "score": 0.8,
            },
        ]

        result = await graph_search(
            {
                "query": "Python",
                "top_k": 5,
            },
            mock_session,
        )

        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) == 2
        assert result["results"][0]["node_id"] == "1"
        assert result["results"][1]["node_id"] == "2"


@pytest.mark.asyncio
async def test_graph_search_missing_query(mock_session: AsyncMock) -> None:
    """Test graph search with missing query."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search({}, mock_session)
    assert exc_info.value.status_code == 400
    assert "Invalid parameters" in str(exc_info.value.detail)
    assert "GraphSearchRequest" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_graph_search_invalid_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with invalid top_k."""
    with pytest.raises(HTTPException) as exc_info:
        await graph_search(
            {
                "query": "Python",
                "top_k": 0,
            },
            mock_session,
        )
    assert exc_info.value.status_code == 400
    assert "top_k must be greater than 0" in str(exc_info.value.detail)


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
    assert exc_info.value.status_code == 400
    assert "Invalid parameters" in str(exc_info.value.detail)
    assert "MatchRoleRequest" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_invalid_experience(mock_session: AsyncMock) -> None:
    """Test role matching with invalid years_experience."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": {"Python": "invalid"},  # Should be int
            },
            mock_session,
        )
    assert exc_info.value.status_code == 400
    assert "Invalid parameters" in str(exc_info.value.detail)
    assert "int_parsing" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_partial_match(mock_session: AsyncMock) -> None:
    """Test role matching with partial skill matches."""
    # Mock the session to return a profile with only some required skills
    mock_result = AsyncMock()
    # The handler expects all required skills to be present in the profile for a match
    # So, if only one skill is present, match_score should be 0.0
    mock_result.fetch_all.return_value = []  # No full matches
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
    mock_result.single.return_value = {
        "s": {"id": "1", "name": "Python"},
        "evidence": [],  # Changed from projects/certifications to evidence
    }
    mock_session.run.return_value = mock_result

    result = await explain_match(
        {"skill_id": "1", "role_requirement": "Python Developer"},
        mock_session,
    )

    assert "explanation" in result
    assert "evidence" in result
    assert len(result["evidence"]) == 0
    assert "0 pieces of evidence" in result["explanation"]


@pytest.mark.asyncio
async def test_explain_match_multiple_evidence(mock_session: AsyncMock) -> None:
    """Test explain match with multiple pieces of evidence."""
    mock_result = AsyncMock()
    mock_result.single.return_value = {
        "s": {"id": "1", "name": "Python"},
        "evidence": [
            {"rel": {"type": "USED_IN"}, "target": {"name": "Project A"}},
            {"rel": {"type": "USED_IN"}, "target": {"name": "Project B"}},
            {"rel": {"type": "USED_IN"}, "target": {"name": "Project C"}},
            {"rel": {"type": "CERTIFIED_IN"}, "target": {"name": "Cert A"}},
            {"rel": {"type": "CERTIFIED_IN"}, "target": {"name": "Cert B"}},
        ],
    }
    mock_session.run.return_value = mock_result

    result = await explain_match(
        {"skill_id": "1", "role_requirement": "Python Developer"},
        mock_session,
    )

    assert len(result["evidence"]) == 5
    assert any("Project A" in str(e["target"]) for e in result["evidence"])
    assert any("Cert A" in str(e["target"]) for e in result["evidence"])


@pytest.mark.asyncio
async def test_explain_match_invalid_skill_id(mock_session: AsyncMock) -> None:
    """Test explain match with invalid skill ID format."""
    with pytest.raises(HTTPException) as exc_info:
        await explain_match(
            {"skill_id": "invalid", "role_requirement": "Python Developer"},
            mock_session,
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_graph_search_empty_results(mock_session: AsyncMock) -> None:
    """Test graph search with no matching results."""
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = []
    mock_session.run.return_value = mock_result

    # Mock embeddings.search to return empty results
    with patch("skill_sphere_mcp.api.mcp.handlers.embeddings.search") as mock_search:
        mock_search.return_value = []
        result = await graph_search({"query": "nonexistent", "top_k": 5}, mock_session)

        assert "results" in result
        assert len(result["results"]) == 0


@pytest.mark.asyncio
async def test_graph_search_special_characters(mock_session: AsyncMock) -> None:
    """Test graph search with special characters in query."""
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = [
        {"n": {"id": "1", "name": "C++", "description": "Programming language"}}
    ]
    mock_session.run.return_value = mock_result

    # Mock embeddings.search to return results
    with patch("skill_sphere_mcp.api.mcp.handlers.embeddings.search") as mock_search:
        mock_search.return_value = [
            {
                "node_id": "1",
                "name": "C++",
                "description": "Programming language",
                "score": 0.9,
            }
        ]
        result = await graph_search({"query": "C++", "top_k": 5}, mock_session)

        assert len(result["results"]) == 1
        assert result["results"][0]["node_id"] == "1"


@pytest.mark.asyncio
async def test_graph_search_large_top_k(mock_session: AsyncMock) -> None:
    """Test graph search with a large top_k value."""
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = [
        {"n": {"id": str(i), "name": f"Node {i}"}} for i in range(100)
    ]
    mock_session.run.return_value = mock_result

    # Mock embeddings.search to return results
    with patch("skill_sphere_mcp.api.mcp.handlers.embeddings.search") as mock_search:
        mock_search.return_value = [
            {"node_id": str(i), "name": f"Node {i}", "score": 0.9} for i in range(100)
        ]
        result = await graph_search({"query": "Node", "top_k": 100}, mock_session)

        assert len(result["results"]) == 100


@pytest.mark.asyncio
async def test_match_role_empty_experience(mock_session: AsyncMock) -> None:
    """Test match role with empty years_experience."""
    mock_skills = [
        {
            "s": {"name": "Python", "id": "1"},
            "relationships": [],
            "experience_years": [5],
        },
        {
            "s": {"name": "FastAPI", "id": "2"},
            "relationships": [],
            "experience_years": [3],
        },
    ]
    with (
        patch(
            "skill_sphere_mcp.api.mcp.handlers._get_skills_with_relationships",
            return_value=mock_skills,
        ),
        patch(
            "skill_sphere_mcp.api.mcp.handlers._calculate_semantic_score",
            return_value=1.0,
        ),
    ):
        result = await match_role(
            {"required_skills": ["Python", "FastAPI"], "years_experience": {}},
            mock_session,
        )
        assert result["match_score"] == 1.0
        assert len(result["matching_skills"]) == 2
        assert len(result["skill_gaps"]) == 0


@pytest.mark.asyncio
async def test_match_role_nonexistent_skills(mock_session: AsyncMock) -> None:
    """Test match role with non-existent skills."""
    mock_result = AsyncMock()
    mock_result.fetch_all.return_value = []
    mock_session.run.return_value = mock_result

    result = await match_role(
        {
            "required_skills": ["NonexistentSkill"],
            "years_experience": {"NonexistentSkill": 5},
        },
        mock_session,
    )

    assert result["match_score"] == 0.0
    assert len(result["matching_skills"]) == 0
    assert len(result["skill_gaps"]) == 1
    assert "NonexistentSkill" in result["skill_gaps"]


@pytest.mark.asyncio
async def test_match_role_multiple_profiles(mock_session: AsyncMock) -> None:
    """Test match role with multiple matching profiles."""
    mock_skills = [
        {
            "s": {"name": "Python", "id": "1"},
            "relationships": [],
            "experience_years": [5],
        },
        {
            "s": {"name": "Python", "id": "2"},
            "relationships": [],
            "experience_years": [3],
        },
    ]
    with (
        patch(
            "skill_sphere_mcp.api.mcp.handlers._get_skills_with_relationships",
            return_value=mock_skills,
        ),
        patch(
            "skill_sphere_mcp.api.mcp.handlers._calculate_semantic_score",
            return_value=1.0,
        ),
    ):
        result = await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": {"Python": 3},
            },
            mock_session,
        )
        assert result["match_score"] == 1.0
        assert len(result["matching_skills"]) == 1
        assert result["matching_skills"][0]["name"] == "Python"


@pytest.mark.asyncio
async def test_match_role_invalid_experience_type(mock_session: AsyncMock) -> None:
    """Test match role with invalid years_experience type."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": "invalid",  # Should be dict
            },
            mock_session,
        )
    assert exc_info.value.status_code == 400
    assert "Input should be a valid dictionary" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_invalid_experience_value(mock_session: AsyncMock) -> None:
    """Test match role with invalid years_experience value."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role(
            {
                "required_skills": ["Python"],
                "years_experience": {"Python": "invalid"},  # Should be int
            },
            mock_session,
        )
    assert exc_info.value.status_code == 400
    assert "Input should be a valid integer" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_match_role_empty_skills(mock_session: AsyncMock) -> None:
    """Test match role with empty required_skills list."""
    with pytest.raises(HTTPException) as exc_info:
        await match_role({"required_skills": [], "years_experience": {}}, mock_session)
    assert exc_info.value.status_code == 400
    assert "required_skills cannot be empty" in str(exc_info.value.detail)
