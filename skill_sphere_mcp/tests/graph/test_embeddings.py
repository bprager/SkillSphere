"""Tests for Node2Vec embeddings and graph search functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
from neo4j import AsyncSession
import networkx as nx
from node2vec import Node2Vec

from skill_sphere_mcp.graph.embeddings import Node2VecEmbeddings, embeddings


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock Neo4j session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_result() -> AsyncMock:
    """Create mock Neo4j result."""
    result = AsyncMock()
    result.__aiter__ = AsyncMock()
    return result


@pytest.fixture
def sample_nodes() -> list[dict]:
    """Create sample node data."""
    return [
        {
            "node_id": 1,
            "labels": ["Skill"],
            "props": {"name": "Python"},
            "edges": [{"target": 2, "type": "RELATES_TO"}],
        },
        {
            "node_id": 2,
            "labels": ["Skill"],
            "props": {"name": "Programming"},
            "edges": [{"target": 1, "type": "RELATES_TO"}],
        },
    ]


@pytest.fixture
def mock_embeddings() -> dict[str, np.ndarray]:
    """Create mock embeddings."""
    return {
        "1": np.random.rand(128),
        "2": np.random.rand(128),
    }


@pytest.mark.asyncio
async def test_embeddings_initialization() -> None:
    """Test Node2VecEmbeddings initialization."""
    emb = Node2VecEmbeddings(dimension=64)
    assert emb.dimension == 64
    assert emb._embeddings == {}
    assert emb._node_ids == {}


@pytest.mark.asyncio
async def test_load_embeddings(
    mock_session: AsyncMock, mock_result: AsyncMock, sample_nodes: list[dict]
) -> None:
    """Test loading embeddings from graph."""
    # Setup mock result
    mock_result.__aiter__.return_value = sample_nodes
    mock_session.run.return_value = mock_result

    # Create embeddings instance
    emb = Node2VecEmbeddings(dimension=128)

    # Mock Node2Vec
    with patch("skill_sphere_mcp.graph.embeddings.Node2Vec") as mock_node2vec:
        mock_model = MagicMock()
        mock_model.wv = {
            "1": np.random.rand(128),
            "2": np.random.rand(128),
        }
        mock_node2vec.return_value.fit.return_value = mock_model

        # Load embeddings
        await emb.load_embeddings(mock_session)

        # Verify session query
        mock_session.run.assert_called_once()
        assert len(emb._embeddings) == 2
        assert len(emb._node_ids) == 2


@pytest.mark.asyncio
async def test_search(
    mock_session: AsyncMock,
    mock_result: AsyncMock,
    sample_nodes: list[dict],
    mock_embeddings: dict[str, np.ndarray],
) -> None:
    """Test similarity search."""
    # Setup mock result for search
    mock_result.single.return_value = {
        "n": MagicMock(),
        "labels": ["Skill"],
        "props": {"name": "Python"},
    }
    mock_session.run.return_value = mock_result

    # Create embeddings instance with mock data
    emb = Node2VecEmbeddings(dimension=128)
    emb._embeddings = mock_embeddings
    emb._node_ids = {"1": 1, "2": 2}

    # Test search
    query_embedding = np.random.rand(128)
    results = await emb.search(mock_session, query_embedding, top_k=1)

    # Verify results
    assert len(results) == 1
    assert "node_id" in results[0]
    assert "score" in results[0]
    assert "labels" in results[0]
    assert "properties" in results[0]


@pytest.mark.asyncio
async def test_search_without_embeddings(
    mock_session: AsyncMock, mock_result: AsyncMock, sample_nodes: list[dict]
) -> None:
    """Test search when embeddings need to be loaded first."""
    # Setup mock result for load_embeddings
    mock_result.__aiter__.return_value = sample_nodes
    mock_session.run.return_value = mock_result

    # Create embeddings instance
    emb = Node2VecEmbeddings(dimension=128)

    # Mock Node2Vec
    with patch("skill_sphere_mcp.graph.embeddings.Node2Vec") as mock_node2vec:
        mock_model = MagicMock()
        mock_model.wv = {
            "1": np.random.rand(128),
            "2": np.random.rand(128),
        }
        mock_node2vec.return_value.fit.return_value = mock_model

        # Test search
        query_embedding = np.random.rand(128)
        results = await emb.search(mock_session, query_embedding, top_k=1)

        # Verify results
        assert len(results) == 1
        assert "node_id" in results[0]
        assert "score" in results[0]


def test_get_embedding(mock_embeddings: dict[str, np.ndarray]) -> None:
    """Test getting embedding for a specific node."""
    emb = Node2VecEmbeddings(dimension=128)
    emb._embeddings = mock_embeddings

    # Test existing node
    embedding = emb.get_embedding("1")
    assert embedding is not None
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (128,)

    # Test non-existing node
    embedding = emb.get_embedding("3")
    assert embedding is None


@pytest.mark.asyncio
async def test_global_embeddings_instance() -> None:
    """Test that the global embeddings instance is properly initialized."""
    # Verify that embeddings is an instance of Node2VecEmbeddings
    assert isinstance(embeddings, Node2VecEmbeddings)
    assert embeddings.dimension == 128
