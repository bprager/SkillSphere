"""Tests for skill matching functionality."""

# pylint: disable=redefined-outer-name, protected-access

from unittest import mock
from unittest.mock import AsyncMock

import numpy as np
import pytest

from skill_sphere_mcp.graph.skill_matching import (MatchResult, SkillMatch,
                                                   SkillMatchingService)

# Test constants
EXPECTED_MATCH_COUNT = 2
EXPECTED_GAP_COUNT = 1
EXPECTED_OVERALL_SCORE = 0.8

# Test data
MOCK_SKILLS = [{"name": "Python", "years": 5}, {"name": "FastAPI", "years": 3}]
MOCK_YEARS = [{"name": "Python", "years": 5}, {"name": "FastAPI", "years": 3}]
MOCK_CANDIDATE_SKILLS = [
    {
        "name": "Python",
        "years": 4,
        "level": "expert",
        "certifications": ["Python Developer"],
    },
    {
        "name": "FastAPI",
        "years": 2,
        "level": "intermediate",
        "certifications": [],
    },
    {
        "name": "Flask",
        "years": 3,
        "level": "intermediate",
        "certifications": [],
    },
]

# Mock data
MOCK_REQUIRED_SKILLS = [{"name": "Python", "years": 5}, {"name": "FastAPI", "years": 3}]
MOCK_CANDIDATE_SKILLS = [
    {"name": "Python", "years": 5},
    {"name": "FastAPI", "years": 3},
]


@pytest.fixture
def skill_matcher() -> SkillMatchingService:
    """Create a skill matching service instance."""
    return SkillMatchingService()


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock()


def test_skill_match_creation() -> None:
    """Test creating a skill match."""
    match = SkillMatch(
        skill_name="Python",
        match_score=0.85,
        experience_years=4,
        evidence=[{"type": "certification", "name": "Python Developer"}],
    )
    assert match.skill_name == "Python"
    assert match.match_score == pytest.approx(0.85)
    assert match.experience_years == pytest.approx(4.0)
    assert match.evidence[0]["name"] == "Python Developer"


def test_match_result_creation() -> None:
    """Test creating a match result."""
    matches = [
        SkillMatch(
            skill_name="Python",
            match_score=0.85,
            experience_years=4,
            evidence=[{"type": "certification", "name": "Python Developer"}],
        ),
        SkillMatch(
            skill_name="FastAPI",
            match_score=0.75,
            experience_years=2,
            evidence=[],
        ),
    ]
    result = MatchResult(
        overall_score=0.8,
        matching_skills=matches,
        skill_gaps=["Django"],
        supporting_nodes=[],
    )
    assert result.overall_score == pytest.approx(EXPECTED_OVERALL_SCORE)
    assert len(result.matching_skills) == EXPECTED_MATCH_COUNT
    assert len(result.skill_gaps) == EXPECTED_GAP_COUNT


@pytest.mark.asyncio
async def test_match_role_success(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test successful role matching."""
    # Patch embeddings.model to a dummy so Node2Vec is not invoked
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))
        mock_session.run.return_value.__aiter__.return_value = [
            {"name": "Python", "years": 5},
            {"name": "FastAPI", "years": 3},
        ]
        result = await skill_matcher.match_role(
            mock_session,
            MOCK_REQUIRED_SKILLS,
            MOCK_CANDIDATE_SKILLS,
        )
        assert result.overall_score > 0
        assert len(result.matching_skills) > 0
        assert len(result.skill_gaps) == 0


@pytest.mark.asyncio
async def test_match_role_no_skills(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test role matching with no skills."""
    result = await skill_matcher.match_role(
        mock_session,
        [],
        [],
    )
    assert result.overall_score == 0
    assert len(result.matching_skills) == 0
    assert len(result.skill_gaps) == 0


@pytest.mark.asyncio
async def test_match_role_no_candidate_skills(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test role matching with no candidate skills."""
    result = await skill_matcher.match_role(
        mock_session,
        MOCK_REQUIRED_SKILLS,
        [],
    )
    assert result.overall_score == 0
    assert len(result.matching_skills) == 0
    assert len(result.skill_gaps) == len(MOCK_REQUIRED_SKILLS)


@pytest.mark.asyncio
async def test_find_best_match(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test finding the best match for a skill."""
    # Patch embeddings.model to a dummy so Node2Vec is not invoked
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))
        mock_session.run.return_value.__aiter__.return_value = [
            {"name": "Python", "years": 5},
        ]
        best_match = await skill_matcher._find_best_match(
            mock_session,
            "Python",
            MOCK_CANDIDATE_SKILLS,
            5.0,
        )
        assert best_match is not None
        assert best_match.skill_name == "Python"
        assert best_match.match_score > 0


@pytest.mark.asyncio
async def test_find_best_match_no_match(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test finding the best match when no match exists."""
    best_match = await skill_matcher._find_best_match(
        mock_session,
        "Rust",
        MOCK_CANDIDATE_SKILLS,
        5.0,
    )
    assert best_match is None


@pytest.mark.asyncio
async def test_get_skill_embedding(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test getting skill embedding."""
    # Patch embeddings.model to a dummy so Node2Vec is not invoked
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones(128)
        # Patch mock_session to simulate DB result with node_id and embedding
        mock_session.run.return_value.single.return_value = {
            "node_id": 1,
            "embedding": np.ones(128),
        }
        embedding = await skill_matcher._get_skill_embedding(mock_session, "Python")
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)


@pytest.mark.asyncio
async def test_gather_evidence(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test gathering evidence for skill match."""
    evidence = await skill_matcher._gather_evidence(mock_session, "Python", "Python")
    assert isinstance(evidence, list)
    assert all(isinstance(item, dict) for item in evidence)
