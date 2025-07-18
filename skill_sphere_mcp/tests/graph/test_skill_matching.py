"""Tests for skill matching functionality."""

# pylint: disable=redefined-outer-name, protected-access

import os
from unittest import mock
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest
import pytest_asyncio

# Clear environment variables before importing settings
os.environ.pop("SKILL_SPHERE_MCP_CLIENT_NAME", None)
os.environ.pop("SKILL_SPHERE_MCP_CLIENT_VERSION", None)
os.environ.pop("SKILL_SPHERE_MCP_CLIENT_ENVIRONMENT", None)
os.environ.pop("SKILL_SPHERE_MCP_CLIENT_FEATURES", None)
os.environ.pop("SKILL_SPHERE_MCP_CLIENT_MCP_INSTRUCTIONS", None)

# Now import the settings
from skill_sphere_mcp.config.settings import ClientInfo, Settings, get_settings
from skill_sphere_mcp.graph.skill_matching import (
    MatchResult,
    SkillMatch,
    SkillMatchingService,
)

# Set test environment
os.environ["PYTEST_CURRENT_TEST"] = "test_skill_matching"

# Initialize test settings
settings = get_settings()

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


@pytest_asyncio.fixture
async def skill_matcher() -> SkillMatchingService:
    """Create a skill matching service instance."""
    return SkillMatchingService()


@pytest_asyncio.fixture
async def mock_session() -> AsyncMock:
    """Create a mock Neo4j session."""
    return AsyncMock()


@pytest.fixture
def mock_settings():
    with patch("skill_sphere_mcp.config.settings.Settings") as mock_settings:
        mock_settings.return_value = Settings(
            client_info=ClientInfo(
                name="TestClient",
                version="1.0.0",
                environment="test",
                features=["cv", "search", "matching", "graph"],
                mcp_instructions="Test instructions",
            )
        )
        yield mock_settings


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

        # Mock a path with nodes and relationships
        mock_node = mock.MagicMock()
        mock_node.labels = ["Skill"]
        mock_node.items.return_value = [("name", "Python")]
        mock_node.get.return_value = (
            "Python"  # Ensure the node can be accessed like a dict
        )

        mock_path = mock.MagicMock()
        mock_path.nodes = [mock_node]
        mock_path.relationships = []

        mock_session.run.return_value.single.return_value = {
            "path": mock_path,
            "node_id": 1,
        }

        result = await skill_matcher.match_role(
            mock_session,
            MOCK_REQUIRED_SKILLS,
            MOCK_CANDIDATE_SKILLS,
        )
        assert result.overall_score > 0
        expected_matching_skills = 2
        assert len(result.matching_skills) == expected_matching_skills
        expected_skill_gaps = 0
        assert len(result.skill_gaps) == expected_skill_gaps


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
async def test_match_role_partial_match(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test role matching with partial skill matches."""
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))
        # Only return a path for the matching skill
        mock_node = mock.MagicMock()
        mock_node.labels = ["Skill"]
        mock_node.get.side_effect = lambda k, default=None: {
            "name": "Python",
            "type": "Programming Language",
        }.get(k, default)
        mock_node.items.return_value = [
            ("name", "Python"),
            ("type", "Programming Language"),
        ]
        mock_path = mock.MagicMock()
        mock_path.nodes = [mock_node]
        mock_path.relationships = []
        # Return node_id for Python embedding, node_id for candidate, path for evidence, None for FastAPI
        mock_session.run.return_value.single.side_effect = [
            {"node_id": 1},  # Python embedding
            {"node_id": 1},  # Python candidate embedding
            {"path": mock_path},  # Python evidence
            None,  # FastAPI embedding (not found)
        ]
        partial_candidate_skills = [{"name": "Python", "years": 5}]
        result = await skill_matcher.match_role(
            mock_session,
            MOCK_REQUIRED_SKILLS,
            partial_candidate_skills,
        )
        # Should only match Python
        assert result.overall_score > 0
        assert len(result.matching_skills) == 1
        assert len(result.skill_gaps) == 1
        assert "FastAPI" in result.skill_gaps


@pytest.mark.asyncio
async def test_match_role_experience_scoring(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test role matching with different experience levels."""
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))

        # Mock a path with nodes and relationships
        mock_node = mock.MagicMock()
        mock_node.labels = ["Skill"]
        mock_node.items.return_value = [("name", "Python")]
        mock_node.get.return_value = (
            "Python"  # Ensure the node can be accessed like a dict
        )

        mock_path = mock.MagicMock()
        mock_path.nodes = [mock_node]
        mock_path.relationships = []

        mock_session.run.return_value.single.return_value = {
            "path": mock_path,
            "node_id": 1,
        }

        # Test with varying experience levels
        candidate_skills = [
            {"name": "Python", "years": 3},  # Less than required
            {"name": "FastAPI", "years": 5},  # More than required
        ]
        result = await skill_matcher.match_role(
            mock_session,
            MOCK_REQUIRED_SKILLS,
            candidate_skills,
        )
        assert result.overall_score > 0
        expected_matching_skills = 2
        assert len(result.matching_skills) == expected_matching_skills
        expected_skill_gaps = 0
        assert len(result.skill_gaps) == expected_skill_gaps


@pytest.mark.asyncio
async def test_find_best_match(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test finding the best match for a skill."""
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))
        mock_node = mock.MagicMock()
        mock_node.labels = ["Skill"]
        mock_node.get.side_effect = lambda k, default=None: {
            "name": "Python",
            "type": "Programming Language",
        }.get(k, default)
        mock_node.items.return_value = [
            ("name", "Python"),
            ("type", "Programming Language"),
        ]
        mock_path = mock.MagicMock()
        mock_path.nodes = [mock_node]
        mock_path.relationships = []

        def run_side_effect(query, *args, **kwargs):
            mock_result = mock.MagicMock()
            if "RETURN id(s) as node_id" in query:
                mock_result.single = AsyncMock(return_value={"node_id": 1})
            elif "RETURN path" in query:
                mock_result.single = AsyncMock(return_value={"path": mock_path})
            else:
                mock_result.single = AsyncMock(return_value=None)
            return mock_result

        mock_session.run.side_effect = run_side_effect

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
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = None
        best_match = await skill_matcher._find_best_match(
            mock_session,
            "Rust",
            MOCK_CANDIDATE_SKILLS,
            5.0,
        )
        assert best_match is None


@pytest.mark.asyncio
async def test_find_best_match_below_threshold(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test finding the best match when similarity is below threshold."""
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))
        mock_node = mock.MagicMock()
        mock_node.labels = ["Skill"]
        mock_node.get.side_effect = lambda k, default=None: {
            "name": "Python",
            "type": "Programming Language",
        }.get(k, default)
        mock_node.items.return_value = [
            ("name", "Python"),
            ("type", "Programming Language"),
        ]
        mock_path = mock.MagicMock()
        mock_path.nodes = [mock_node]
        mock_path.relationships = []

        def run_side_effect(query, *args, **kwargs):
            mock_result = mock.MagicMock()
            if "RETURN id(s) as node_id" in query:
                mock_result.single = AsyncMock(return_value={"node_id": 1})
            elif "RETURN path" in query:
                mock_result.single = AsyncMock(return_value={"path": mock_path})
            else:
                mock_result.single = AsyncMock(return_value=None)
            return mock_result

        mock_session.run.side_effect = run_side_effect

        # Create a matcher with high threshold
        high_threshold_matcher = SkillMatchingService(similarity_threshold=1.1)
        best_match = await high_threshold_matcher._find_best_match(
            mock_session,
            "Python",
            MOCK_CANDIDATE_SKILLS,
            5.0,
        )
        assert best_match is None


@pytest.mark.asyncio
async def test_get_skill_embedding(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test getting skill embedding."""
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones(128)
        mock_session.run.return_value.single.return_value = {"node_id": 1}
        embedding = await skill_matcher._get_skill_embedding(mock_session, "Python")
        assert embedding is not None
        assert isinstance(embedding, np.ndarray)


@pytest.mark.asyncio
async def test_get_skill_embedding_not_found(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test getting skill embedding when skill is not found."""
    mock_session.run.return_value.single.return_value = None
    embedding = await skill_matcher._get_skill_embedding(mock_session, "UnknownSkill")
    assert embedding is None


@pytest.mark.asyncio
async def test_gather_evidence(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test gathering evidence for skill match."""
    # Mock a path with nodes and relationships
    mock_node = mock.MagicMock()
    mock_node.labels = ["Skill"]
    mock_node.get.side_effect = lambda k, default=None: {
        "name": "Python",
        "type": "Programming Language",
    }.get(k, default)
    mock_node.items.return_value = [
        ("name", "Python"),
        ("type", "Programming Language"),
    ]

    mock_path = mock.MagicMock()
    mock_path.nodes = [mock_node]
    mock_path.relationships = []

    mock_session.run.return_value.single.return_value = {"path": mock_path}

    evidence = await skill_matcher._gather_evidence(mock_session, "Python", "Python")
    assert isinstance(evidence, list)
    assert len(evidence) > 0
    assert evidence[0]["type"] == "node"
    assert "Python" in evidence[0]["properties"].values()


@pytest.mark.asyncio
async def test_gather_evidence_no_path(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test gathering evidence when no path exists."""
    mock_session.run.return_value.single.return_value = None
    evidence = await skill_matcher._gather_evidence(mock_session, "Python", "Rust")
    assert isinstance(evidence, list)
    assert len(evidence) == 0


@pytest.mark.asyncio
async def test_match_role_with_evidence(
    skill_matcher: SkillMatchingService, mock_session: AsyncMock
) -> None:
    """Test role matching with evidence gathering."""
    with mock.patch(
        "skill_sphere_mcp.graph.skill_matching.embeddings"
    ) as mock_embeddings:
        mock_embeddings.model = object()
        mock_embeddings.get_embedding.return_value = np.ones((1, 128))
        mock_node = mock.MagicMock()
        mock_node.labels = ["Skill"]
        mock_node.get.side_effect = lambda k, default=None: {
            "name": "Python",
            "type": "Programming Language",
        }.get(k, default)
        mock_node.items.return_value = [
            ("name", "Python"),
            ("type", "Programming Language"),
        ]
        mock_path = mock.MagicMock()
        mock_path.nodes = [mock_node]
        mock_path.relationships = []
        # First call for embedding, second for evidence
        mock_session.run.return_value.single.side_effect = [
            {"node_id": 1},  # embedding for req_skill
            {"node_id": 1},  # embedding for candidate
            {"path": mock_path},  # evidence
        ]
        result = await skill_matcher.match_role(
            mock_session,
            [{"name": "Python", "years": 5}],
            [{"name": "Python", "years": 4}],
        )
        assert result.overall_score > 0
        assert len(result.matching_skills) == 1
        assert len(result.matching_skills[0].evidence) > 0
        assert result.supporting_nodes
